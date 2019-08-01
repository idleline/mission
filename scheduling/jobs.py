'''
    : mission.scheduling.jobs :
    
    Module for job schedules.
    
    It's recommended to put new jobs in their own file. This
    prevents namespace collision, poorly written functions,
    or broken imports from causing the entire module to fail.
    
    Only put functions in here if necessary.
'''
# System level imports
import requests
import simplejson as json

# Application level imports
from mission import dprint, q
from mission.lib.logconfig import applog, errlog
from mission.lib.notify import notify_admins
'''
    : Check Scheduler :
    
    Simple job to check status of scheduler
'''
def check_scheduler():
    ''' Default Job for Scheduler Verification '''
    
    message_data = {'title' : 'Scheduler Status', 'body' : '' }
    
    r = requests.get(url='http://127.0.0.1:5000/scheduler')
    
    try:
        response = json.loads(r.text)
    except Exception as e:
        q.put(e)
        message_data['body'] = 'Exception'
        notify_admins(message_data)
    
    try:
        if response['running']:
            message_data['body'] = "Running"
        
        else:
            message_data['body'] = "Paused"
        
    except Exception as e:
        q.put(e)
        message_data['body'] = 'Exception'
        return None
    
    q.put('Finished. Scheduler is {0}'.format(message_data['body']))