'''
    mission.admin.user
    
    Module for handling user administration functions
'''
# System dependencies
import re, uuid, smtplib, dkim
import simplejson as json
from os import listdir
from os.path import isfile, join
from bcrypt import hashpw, checkpw, gensalt
from bs4 import BeautifulSoup
from dns import resolver, query, name
from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Flask application imports
from flask import flash, render_template, request, make_response, jsonify
from flask_security import current_user

# Application level dependencies
from mission import dprint, scheduler
from mission.mod_auth.controllers import user_datastore
from mission.mod_auth.models import User, Role, UserGroup, UserProfile, Notification, ValidateEmail
from mission.lib.database import db_session
from mission.lib.logconfig import applog, errlog

# Import Exceptions
import werkzeug.exceptions
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError

# Constants
failed = 'failed'

def user_list():

    return User.query.all()

def list_roles():
    
    return Role.query.all()

def get_schedule():
    
    if scheduler.running:
        resp = {'status' : 'Started', 'state' : 'start', 'toggle' : 'pause' }
    else:
        resp = {'status' : 'Paused', 'state' : 'pause', 'toggle' : 'start' }

    return resp

def job_list():
    ''' Get a list of all potential jobs '''

    """
        : PATH :
        
        Set path to find scheduling python modules and regex pattern
        to parse for functions. Store functions in a dict object.
        
        @param {result_set}     Dict object with functions
        
        Classes and methods not supported yet. 
    """
    mypath = 'mission/scheduling'
    func_regex = "(?<=def\s)[^\(]+"

    result_set = {}

    """
        Iterate through *.py files in the directory for job scheduling
    """
    for mod in [f for f in listdir(mypath) if isfile(join(mypath, f))]:

        mod_file_re = '.+\.py$'

        if re.match(mod_file_re, mod) and mod != '__init__.py':
            mod_name = mod.split('.')[0]

            with open(mypath+'/'+mod) as fdata:
                data = fdata.read()

            result_set[mod_name] = re.findall(func_regex, data)
    
    return result_set

def user_edit(req):
    ''' Edit user in administrative view '''
    status = None

    user_keys = ['username', 'role', 'value']
    
    for k in user_keys:
        if k not in req.json.keys():
            return make_response(jsonify(
                status = 'error',
                message = 'Invalid JSON',
                ), 200)

    username = req.json['username']
    rolename = req.json['role']
    value = req.json['value']
    
    user = user_datastore.find_user(username=username)
    
    if not user:
        status = 'error'
        message = 'Invalid user parameters'
    
    if user.username == current_user.username and not current_user.has_role('superuser'):
        status = 'error'
        message = 'Cannot edit current user'
    
    role = user_datastore.find_role(rolename)
    
    if not role:
        status = 'error'
        message = 'Invalid role selection'
    
    if not status:
        try:
            if value is False:
                user_datastore.remove_role_from_user(user,role)
                user_datastore.commit()
                status = 'success'
                message = 'Removed user {0} from {1}'.format(username,rolename)
            
            elif value is True:
                user_datastore.add_role_to_user(user,role)
                user_datastore.commit()
                status = 'success'
                message = 'Added user {0} to {1}'.format(username,rolename)
            
            else:
                status = 'error'
                message = 'Invalid value for selection'
        
        except Exception as err:
            dprint(err)
            status = 'error'
            message = 'Failed to update'
    
    return make_response(jsonify(
        status = status,
        message = message,
        ), 200)

def create_new_user(request):
    ''' Create a new user for the site '''
    
    if hasattr(request, 'json'):
        form_data = request.json
    elif hasattr(request, 'form'):
        form_data = request.form
    else:
        return make_response(jsonify(
        status = 'failed',
        message = 'Request object invalid',
        ), 404)
    
    for key, value in request.json.items():
        attr = key.split('-')[-1]
        globals()[attr] = value
    
    user_datastore.create_user(
        firstname = firstname,
        lastname = lastname, 
        username = username,
        email = email,
        password = hashpw(str(password), gensalt(13))
    )
    
    """"
        : CRUD NEW USER :
        
        Attempt to write new user to the SQL engine user_datastore. Catch
        for duplicates.
    """
    try:
    
        user_datastore.commit()
        status = 'success'
        message = 'Created new user'
        applog.info('{0} - {1}'.format(message, username))
        code = 200
    
    except IntegrityError as e:
        message = 'Failed to create new user {0} with error'.format(username)
        applog.error('{0} - {1}'.format(message, e))
        status = failed
        message = message
        code = 404
    
    user = user_datastore.find_user(username=username)
    
    applog.info('Sending activation e-mail')
    send_activation_email(user)

    applog.info('Creating User Profile')    
    create_user_profile(user)
    
    status = 'success'
    message = 'New user created & Activation sent'
    code = 200
    
    return make_response(jsonify(
        status = status,
        message = message,
        ), code)

def create_user_profile(user):
    
    profile = UserProfile(user=user)
    
    db_session.add(profile)
    db_session.commit()

    return 

def send_activation_email(user):
    ''' Send an activation email to new user '''
    
    """
        : CONSTANTS :
        
        This function should only be called by create_user. Any other use would have unexpected results.
        
        @param {noreply}                    Return address
        @param {mail_domain}                Domain sending e-mail with DKIM signature
        @param {dkim_private_key_file}      Private Key for DKIM signatures
        @param {dkim_selector}              DNS record for DKIM validation
    """
    base_url = 'https://mission.idleline.io/'
    noreply = "Mission House <noreply@idleline.io>"
    mail_domain = 'idleline.io'
    dkim_private_key_file = "mhapp._domainkey.idleline.io.key"
    dkim_selector = "mhapp"
    
    """
        : GENERATE UIDS : 
        
        Set up UIDs to track user requests
    """
    vid = uuid.uuid4()
    eid = uuid.uuid5(uuid.NAMESPACE_OID, str(user.email))

    """
        : SET UP VALIDATION : 
        
        Create database object for validating user in subsequent requests
    """    
    v = ValidateEmail(
        created = datetime.now(), 
        user = user.id, 
        eid = eid,
        vid = vid,
        activated = False,
    )    

    db_session.add(v)
    db_session.commit()
    
    """
        : FORMAT E-MAIL :
        
        Add in the attributes to HTML message body needed to validate the user or unsubscribe
    """
    with open('mission/templates/email-pretty.html', 'r') as fo:
        data = fo.read()

    soup = BeautifulSoup(data, 'html.parser')
    
    ''' Create validation link '''
    soup.find('a', attrs={'id' : 'validate'})['href'] = '{0}validate?vid={1}&eid={2}'.format(base_url, vid, eid)

    ''' Create unsubscribe link '''
    soup.find('a', attrs={'id' : 'unsub'})['href'] = '{0}unsubscribe?eid={1}'.format(base_url, eid)

    ''' Email personalization footer '''
    soup.find('td', attrs={'id' : 'sentto'})['text'] = "We sent this to {0}".format(User.username)

    msg_body = soup.encode_contents(formatter='html')
    
    """
        : SMTP SETUP :
        
        @param {mtas}       List object of valid MTAs for a domain
    """
    mtas = find_mta_from_email(user.email)

    fromaddr = noreply
    toaddr = user.email
    subject = 'Please validate your e-mail address to continue registration'

    ''' MIME & HTML Body Crafting '''    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(msg_body, 'HTML'))
    text = msg.as_string()

    ''' DKIM SIGNATURE '''
    with open(dkim_private_key_file) as pkf:
        dkim_private_key = pkf.read()
        
        headers = ["To", "From", "Subject"]
        sig = dkim.sign(
            message = text,
            selector = dkim_selector,
            domain = 'idleline.io',
            privkey = dkim_private_key.strip(),
            include_headers = headers
        )
        msg['DKIM-Signature'] = sig.lstrip("DKIM-Signature: ")
    
    ''' SMTP SERVER CONNECTION '''
    for mta in mtas:
        
        try:
            s = smtplib.SMTP(mta['mta'], 25)
            #s.set_debuglevel(1)
            s.ehlo()
            s.starttls()
            s.ehlo()
        
            s.sendmail(fromaddr, toaddr, text) 
        
            applog.info('Activation mail sent')
            return True
        
        except Exception as e:
            applog.error('Encountered an error: {0}'.format(e))
            return False
    

def find_mta_from_email(email):
    ''' Return MTAs for a mail domain '''

    mail_domain = email.split('@')[-1]
    
    mtas = []
    
    answers = resolver.query(mail_domain, 'MX')
    
    for rdata in answers:
        mtas.append({
            'mta' : rdata.exchange.to_text(),
            'pref': rdata.preference,
        })
    
    return mtas

def delete_user(request):
    
    applog.debug('Received delete user request')
    user = user_datastore.find_user(username = request.json['username'])
    
    applog.info('Found user to delete')
    
    if user:
        
        if user.username == current_user.username:
            status = 'failed'
            message = 'Cannot delete current user'
            code = 404
        
        else:
            applog.info('User deletion passed validation checks')
            user_datastore.delete_user(user)
            user_datastore.commit()
            
            applog.info('User {0} deleted'.format(user.username))
            
            status = 'success'
            message = 'User successfully deleted'
            code = 200
    
    else:
        status = 'failed',
        message = 'Unable to delete user'
        code = 404

    return make_response(jsonify(
        status = status,
        message = message,
        ), code)

def edit_user(request):
    ''' Administrator request to delete a user '''
    
    '''
        :: Form Validation ::
        
        @param {user_data}      Leverages validation to ensure user form
                                is complete.
    '''
    user_data = validateUser(request)
    
    if not user_data:
        return make_response(jsonify(
                status = 'failed',
                message = ' Invalid User Parameters'), 200)
    '''
        :: User Identity ::
        
        @param {edit-user}      Retrieve user object from DB based on user-email
        
        User lookup 
        
        :TODO: Sanitation & Error checking for user
    '''
    edit_user = user_datastore.find_user(username=user_data.email)
    
    if not edit_user:
        return make_response(jsonify(
                status = 'failed',
                message = ' User not found'), 200)
    
    dprint('Editing', edit_user.username)
    '''
        :: Activation ::
        
        @param {active}     Boolean flag for user enablement
    
    '''
    if request.json['active'] == False:
        user_datastore.deactivate_user(edit_user)
                
    elif request.json['active'] == True:
        user_datastore.activate_user(edit_user)
    
    user_datastore.commit()
    
    '''
        :: Success ::
        
        Return a 200 if no errors were encountered
    '''
    
    return make_response(jsonify(
        status = 'success',
        message = ' Modified {0} {1}'.format(edit_user.firstname, edit_user.lastname)
        ), 200)

def modify_user_role(request):
    ''' Add or Remove Role for User '''
    
    if not hasattr(request, 'json'):
        return make_response(jsonify(
            status = 'failed',
            message = ' Invalid User Parameters'), 200) 
    
    data = request.json   
    
    for a in ['username', 'role', 'action']:
        if a not in data.keys():
            return make_response(jsonify(
                status = 'failed',
                message = 'Bad attributes'), 200)
    
    user = user_datastore.find_user(username=data['username'])
    
    if not user:
        return make_response(jsonify(
            status = 'failed',
            message = 'Unknown user'), 200)
    
    action = data['action']
    role = data['role']
    
    if action == 'add':    
        result = user_datastore.add_role_to_user(user, role)
    elif action == 'remove':
        if len(current_user.roles) < 2 and role == 'superuser':
            result = False
        else:
            result = user_datastore.remove_role_from_user(user, role)
    
    if result is True:
        applog.info('User modification: {0} - {1} - {2}'.format(user.username, action, role))
        user_datastore.commit()
        
        return make_response(jsonify(
            status = 'success',
            message = "Modified {0} role ({1}) for {2}'s account".format(role, action, user.username)
        ), 200)
    
    else:
        applog.info('[FAILED] User Modification: {0} - {1} - {2}'.format(user.username, action, role))
        
        return make_response(jsonify(
            status = 'failed',
            message = "Unable to modify user",
        ), 200)

def list_user_groups(req):
    ''' Return All User Groups '''
    
    group_list = []
    groups = UserGroup.query.all()
    
    for g in groups:
        group = {
            'name' : g.name, 
            'default_role' : g.default_role.name,
            'description' : g.default_role.description,
        }
        group_list.append(group)
    
    return make_response(jsonify(
        status = 'success',
        draw = req.json['draw'],
        recordsTotal = len(group_list),
        recordsFiltered = len(group_list),
        data = group_list,
        ), 200)

"""
    : VALIDATION FUNCTIONS :
"""
def validate_new_username(request, ajax=True):
    ''' Check if username exists already '''
    
    if User.query.filter(User.username == request.json['username']).first():
        exists = True
        status = 'failed'
        message = "Username exists already"
        code = 404
        
    else:
        exists = False
        status = 'success'
        message = 'Username available'
        code = 202
     
    if ajax is True:
        return make_response(jsonify(
            status = status,
            message = message,
        ), code)
    
    else:
        return exists
    
def validate_new_email(request, ajax=True):
    ''' Check if email address exists already '''

    if User.query.filter(User.email == request.json['email']).first():
        exists = True
        status = 'failed'
        message = "Email address exists already"
        code = 404
        
    else:
        exists = False
        status = 'success'
        message = None,
        code = 202
     
    if ajax is True:
        return make_response(jsonify(
            status = status,
            message = message,
        ), code)
    
    else:
        return exists

def validate_new_password(request, ajax=True):
    ''' Check if email address exists already '''
    
    return None
    
    
"""
    : USER PROFILE FUNCTIONS :
"""
def user_profile():
    ''' Return User Profile '''
    
    ''' 
        :: User Identity ::
        
        Grab current user from flask_security & their attribute roles. We
        are trusting flask to track users correctly. No additional checks
        are in place. This could be a problem and is a todo item.
        
        :TODO: Implement stricter checks on user identity
    '''
    roles = [role.name for role in current_user.roles ]
    
    '''
        :: Render Page ::
        
        Display page for user
    '''
    if request.method == "GET":
        return render_template('profile.html', user=current_user, roles=','.join(roles))

def send_response():
    ''' Return the admin template '''
    
    render_template('admin.html', form=request.form)