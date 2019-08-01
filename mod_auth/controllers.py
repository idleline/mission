'''
    mission.mod_auth.controllers
    
    Authentication controller
'''
# Import Python dependencies
import urllib, traceback

# Import Flask dependencies
from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify, send_from_directory, current_app, make_response
from flask_security import login_required, login_user, logout_user, current_user, roles_required, SQLAlchemyUserDatastore
from flask_security.core import AnonymousUser
from flask_security.utils import encrypt_password

# Import application database object
from mission import dprint

# Import database models
from mission.mod_auth.models import User, Role, UserGroup
from mission.lib.database import db_session, init_db
from mission.lib.logconfig import applog, errlog

# Register the auth blueprint for auth
mod_auth = Blueprint('auth', __name__)

# Configure our User datastore object
user_datastore = SQLAlchemyUserDatastore(db_session, User, Role)
user_datastore.db.session = db_session

# Import security controllers
from mission.lib.auth import authorize_user, validate_password, render_login_page, hash_user_password
from mission.mod_auth.userprofile import find_user_notifications, update_notice

'''
    
    : Create Template User :


try:
    applog.info('Adding new user')
    user_datastore.create_user(username='lwheelock', email='lawheelock@gmail.com', password=hash_user_password('mission platter'))
    user_datastore.commit()
    applog.info('Added new user')
    
except Exception as e:
    applog.error('New User failed: {0}'.format(e))
'''

@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    ''' Primary login view for mission '''
    
    dprint('login flow started')
    
    try:
        next = request.args.get('next')
    except Exception as e:
        applog.error('mission.mod_auth.login: [next] {0}'.format(e))

    """
        :: Login ::
        
        Check if user is authenticated. Redirect to the search
        view if user is. If user is not, evaluate based on HTTP Method.

        GET     Render login page
        POST    Sanitize input and authenticate user from supplied credentials
        HEAD    Empty response

        If user is successful apply the flask_security.login_user function and
        set the session state. Then redirect to search.

    """
    # Redirect to index for authenticated user
    if current_user.is_authenticated is True:
        return redirect(url_for('dashboard.index'))
        #return redirect(next or url_for('dashboard.index'))
    
    # Render login page 
    if request.method == 'GET':
        return render_login_page()
    
    # Empty response header for HEAD requests to /login
    if request.method == 'HEAD':
        return make_response('', 200)

    """
        : Fetch Form Details : 
        
        Init objects for username & password from the request object form attribute.
        
        Catch various errors that may arise from client provided data
    """
    try: 
        username = request.form['username']
        password = request.form['password']
    
    except AttributeError as e:
        applog.error('Request attribute error when parsing form: {0}'.format(e))

        return render_login_page(error='Bad Request')
        
    except TypeError as e:
        applog.error('Request type error when parsing form: {0}'.format(e))

        return render_login_page(error='Invalid Data')
        
    except KeyError as e:
        applog.error('Request key error when parsing form: {0}'.format(e))
        
        return render_login_page(error='Missing Data')
    
    except Exception as e:
        applog.error('Unknown Error: {0}'.format(e))
        
        return render_login_page(error='Error')

    """
        : Login User :
        
        Initialize the session in Flask Security for user object. Redirect user
        to the {next} URL or the index page.
    """
    user = user_datastore.find_user(username=username)
    
    try:     
        applog.info('Validating user {0}'.format(username))
        
        if user is None:
            applog.warning('Unknown user attempting to login: {0}'.format(username))

            return render_login_page(error='Invalid user')

        elif validate_password(user, request) is True:
            applog.info('User logged in: {0}'.format(username))
            login_user(user)
            user_datastore.commit()
            
            #return redirect(next or url_for('dashboard.index'))
            applog.info('{0} is Authenticated: {1} - Redirecting to dashboard'.format(user.username, current_user.is_authenticated))
            return redirect(url_for('dashboard.index'))
        
        else: 
            applog.warning('Unable to validate user password: {0}'.format(username))

    except Exception as e:
        errlog.debug('Attempting to roll back user datastore SQL session')
        user_datastore.db.session.rollback()
        errlog.debug('Rolled back session user datastore SQL session: {0}'.format(e))

    """
        : Default Render :
        
        If no conditions are met, return a general failure and render the login page again
        
    """
    return render_template('auth.html', error='Invalid Login')
    
@mod_auth.route('/logout', methods=['GET', 'POST'])
def logout():
    ''' Log out current user '''
    
    if current_user.is_anonymous:
        return render_login_page(error='Not Logged In')
    
    applog.info('{0} logged out'.format(current_user.id))
    
    logout_user()
    
    return render_login_page(error="Logged Out", level='info')

'''
    ::Administration and User ::
    
    Functions for maintaining the site and access
'''
@mod_auth.route('/user/notifications', methods=['POST'])
def retrieve_notifications():
    ''' Read User Notifications '''
    
    return find_user_notifications(request)
    
@mod_auth.route('/user/notifications/read/<string:notice>', methods=['POST'])
@login_required
def read_notification(notice=None):
    ''' Set notice to read '''
    
    return update_notice(request, notice)

@mod_auth.route('/api/v1/generate_token', methods=['POST'])
def api_generate_token():
    ''' Request a Token Generated '''
    
    if not request.json:
        return make_response(jsonify({'status' : 'error', 'message' : 'Invalid request'}))
    
    username = request.json['username']
    password = request.json['password']
    
    role = Role.query.filter(Role.name==request.json['role']).first()
    
    if user_datastore.find_user(username=username):
        return make_response(jsonify({'status' : 'error', 'message' : 'User already exists'}))
    
    user_datastore.create_user(
        username = username,
        password = encrypt_password(password), 
        active = False, 
        roles = [role],
    )
    
    user_datastore.commit()

    return make_response(jsonify({'status' : 'success'}))
