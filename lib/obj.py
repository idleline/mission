'''
    dmarc.lib.obj
    
    Constants, classes, and functions for dmarc application.
    
'''
# Python system dependency imports
import datetime, pytz, uuid, requests, re, subprocess, urllib, re, socket
import simplejson as json
from requests.exceptions import ChunkedEncodingError
from apscheduler.triggers import *
from dateutil import parser
import ipaddress

# dmarc dependency imports
from dmarc import dprint, root_path
from dmarc.lib.models import *
from dmarc.lib.logconfig import applog, errlog

'''
    :Constants:
   
    Time objects needed to create window for targeted searching through time.
    Accurate time windows decrease search time and reduce the chance the 
    search exceeds the 60 second mark with no found packets. This means we
    will have more chance to get returned data without the API call timing out.
    
    An alternative would be to ask CPacket to make the timeout configurable.
    
    @param {epoch}  Time in seconds from epoch (utc)
'''
epoch = datetime.datetime.utcfromtimestamp(0)
epoch = epoch.replace(tzinfo=pytz.utc)

def convert_to_epoch(datetime_obj):
    ''' Convert date to epoch seconds for cStor API call '''
    
    return int((datetime_obj - epoch).total_seconds())

'''
    : Class Objects : 
'''
class IP(object):
    ''' Object for Handling IP objects in Blacklists '''

    def __init__(self, data):
        
        attrs = ['ipaddress.ip_address', 'comment', 'op']
        
        if not isinstance(data, dict):
            t = "Expected JSON object got '{0}'".format(type(data))
            raise TypeError(t)
        
        for a in attrs:
            if a not in data.keys():
                e = "Missing paramaters"
                raise ValueError(e)        
            
            setattr(self, a, data[a])       

class JSONData(object):
    def __init__(self, status, msgType, msg, data=None, **kwargs):
        self.status = status
        self.msgType = msgType
        self.msg = msg
        self.data = data
        
        self._set_message()
        
        for k,v in kwargs.items():
            setattr(self, k, v)
    
    def _set_message(self):
        self.message = '{0}: {1}'.format(self.msgType, self.msg)

'''
    : Utility Functions :
'''
            
def parse_ip(ip):
    ''' Parse IP object for validity '''
    
    '''
        : Regular Expression Match :
        
        Check the IP address provided for a regular expression match to a
        pattern consistent with being an IP Address. The try / catch block
        here is redundant and should be removed if the regex is confident. 
        
        @param {ipregex}    Regular expression pattern for a valid IP address
        @class {ipaddress.ip_address}  from netaddr library
    '''
    ipregex = '^10\.(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    if re.match(ipregex, ip):
        try:
            ip = ipaddress.ip_address(ip)
    
        except ValueError as e:
            errlog.error('[dmarc.lib.obj.parse_ip],{0},{1}'.format(ip,e))
            return None

        '''
            : DNS Resolution :
            
            If not an IP address, attempt to resolve the IP through DNS resolution
            using the socket library. This block needs additional validation of the
            client input to mitigate vulnerabilities in socket. 
            
            @param {attrs}      Valid attributes for the form data
        '''            
    else:
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(ip))
        
        except socket.gaierror as e:
            errlog.error('[dmarc.lib.obj.parse_ip],{0},{1}'.format(ip,e))
            return None

    return ip


    
def valid_tld(tld):
    tld = tld.lower()
    
    if TLD.query.filter(TLD.name==tld).first():
        return True
    
    return False

def is_ip(address_object):
    ''' Determines if this object an IP '''
    
    ipregex = '^10\.(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    ip = address_object.split('/')[0]
        
    if re.match(ipregex, ip):
        return True

    return False

def is_hostname(address_object):
    ''' Determines if object is a hostname '''
    
    fqdn = address_object.split('.')
    
    if len(fqdn) < 2:
        return False
        
    subs, root, tld = fqdn[:-2], fqdn[-2], fqdn[-1]
    
    if not valid_tld(tld):
        return False
    
    return True


'''
    :Class Definitions:
    
    %class  {SearchQuery}       Object for storing & normalizing attributes provided by the
                                client. Not necessarily any validation performed at this
                                level
'''
"""
class UserAuth(object):
    ''' Class for Login Handling '''
    
    def __init__(self, login):
        try:
            for k,v in login.items():
                setattr(self, k, v)
                
            self.password = self.password.encode('utf-8')
        
        except Exception as e:
            self.error = e
                    
    def ispw(self, hashval):
        if bcrypt.hashpw(self.password, hashval) == hashval:
            return True
        else:
            return False
    
    def hashpw(self):
        return setattr(self, 'hashpw', bcrypt.hashpw(self.password, bcrypt.gensalt()))
     
    def _encoded(self):
        return str(self.password).encode('utf-8')

class TokenRequest(object):
    def __init__(self, json):
        self.json = json
        
        def _set_attrs(self):
            params = ['username', 'password', 'role']
            
            for p in params:
                setattr(self, p, self.json[p])
    
class LDAPUserAuth(object):
    ''' Class for Login Handling '''
    
    def __init__(self, email):
        self.email = email

class Notify(object):
    def __init__(self, name, item, info):
        self.id = uuid.uuid4()
        self.name = name
        self.item = item
        self.info = info

class JSONData(object):
    def __init__(self, status, msgType, msg, data=None, **kwargs):
        self.status = status
        self.msgType = msgType
        self.msg = msg
        self.data = data
        
        self._set_message()
        
        for k,v in kwargs.items():
            setattr(self, k, v)
    
    def _set_message(self):
        self.message = '{0}: {1}'.format(self.msgType, self.msg)

class Job(object):
    def __init__(self, job):
        self.id = job.id
        self.name = job.name
        self.func = job.func.func_name
        self.args = job.args
        self.start_date = job.trigger.start_date.strftime("%b %d %Y %H:%M:%S")
        self.interval = job.trigger.interval.seconds
        self.pending = job.pending
        self.trigger = self._get_trigger(job.trigger)       
        self.next_run = self._next_run(job)

        self.response = self._response()
    
    def _response(self):
        d = { 
            'id' : self.id,
            'name' : self.name,
            'func' : self.func,
            'args' : self.args,
            'start_date' : self.start_date,
            'seconds'  : self.interval,
            'trigger'   : self.trigger,
            'pending'   : self.pending,
            'next_run' : self.next_run,
        }
    
        return d
        
    def _get_trigger(self, t):
        
        return t.__class__.__name__.split('T')[0] 
    
    def _next_run(self, job):
        if job.next_run_time:
            return job.next_run_time.strftime("%b %d %Y %H:%M:%S")
        else:
            return 'Paused'

class Page(object):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class IP(object):
    ''' Object for Handling IP objects in Blacklists '''

    def __init__(self, data):
        
        attrs = ['ipaddress.ip_address', 'comment', 'op']
        
        if not isinstance(data, dict):
            t = "Expected JSON object got '{0}'".format(type(data))
            raise TypeError(t)
        
        for a in attrs:
            if a not in data.keys():
                e = "Missing paramaters"
                raise ValueError(e)        
            
            setattr(self, a, data[a])                

'''
    :Functions:
    
    dmarc.lib.obj function definition for the primary logic needed by the view
    handlers.
    
    Function definition and documentation provided in docstrings and comments. 
'''
def convert_to_epoch(datetime_obj):
    ''' Convert date to epoch seconds for cStor API call '''
    
    return int((datetime_obj - epoch).total_seconds())
    
def valid_tld(tld):
    tld = tld.lower()
    
    if TLD.query.filter(TLD.name==tld).first():
        return True
    
    return False

def is_ip(address_object):
    ''' Determines if this object an IP '''
    
    ipregex = '^10\.(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    ip = address_object.split('/')[0]
        
    if re.match(ipregex, ip):
        return True

    return False

def is_hostname(address_object):
    ''' Determines if object is a hostname '''
    
    fqdn = address_object.split('.')
    
    if len(fqdn) < 2:
        return False
        
    subs, root, tld = fqdn[:-2], fqdn[-2], fqdn[-1]
    
    if not valid_tld(tld):
        return False
    
    return True

def parse_ip(ip):
    ''' Parse IP object for validity '''
    
    '''
        : Regular Expression Match :
        
        Check the IP address provided for a regular expression match to a
        pattern consistent with being an IP Address. The try / catch block
        here is redundant and should be removed if the regex is confident. 
        
        @param {ipregex}    Regular expression pattern for a valid IP address
        @class {ipaddress.ip_address}  from netaddr library
    '''
    ipregex = '^10\.(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    if re.match(ipregex, ip):
        try:
            ip = ipaddress.ip_address(ip)
    
        except ValueError as e:
            errlog.error('[dmarc.lib.obj.parse_ip],{0},{1}'.format(ip,e))
            return None

        '''
            : DNS Resolution :
            
            If not an IP address, attempt to resolve the IP through DNS resolution
            using the socket library. This block needs additional validation of the
            client input to mitigate vulnerabilities in socket. 
            
            @param {attrs}      Valid attributes for the form data
        '''            
    else:
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(ip))
        
        except socket.gaierror as e:
            errlog.error('[dmarc.lib.obj.parse_ip],{0},{1}'.format(ip,e))
            return None

    return ip

def validateUser(data):

    attrs = ['active', 'edit-firstname', 'edit-lastname', 'edit-email']
    dprint(data.json)

    if hasattr(data, 'json') is False:
        raise werkzeug.exceptions.BadRequest('Invalid request')

    for a in attrs:
        if data.json.has_key(a) is False:
            raise werkzeug.exceptions.BadRequest('Invalid request')

    edit_user = UserEdit()

    for k, v in data.json.items():
        try:
            k = k.split('-')[1]
        except IndexError:
            pass

        dprint('setting', k, 'to', v)

        setattr(edit_user, k, v)

    dprint('returning')

    return edit_user

def is_reserved_address_space(address_object):
    ''' Check if the IP belongs to any reserved groups '''
    
    reserved_ip_object = reserved_ip(address_object)
    
    if reserved_ip_object:
        return reserved_ip_object 
    
    reserved_net_object = reserved_net(address_object)
    
    if reserved_net(address_object):
        return reserved_net_object
    
    return None
    
def reserved_ip(ip):
    ''' Reserved IPs '''
    
    reserved_ips = ReservedIP.query.all()
    
    for rip in reserved_ips:
        if ip == rip.ipaddr:
            return ip
    
    return None
    
def reserved_net(net):
    ''' Reserved Networks '''

    reserved_nets = ReservedNetwork.query.all()
    
    for rnet in reserved_nets:
        if ipaddress.ip_network(net) in ipaddress.ip_network(rnet.ipaddr):
            return rnet
            
    return None
"""