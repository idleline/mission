'''
    dmarc.lib.logconfig
'''
# Configure Logging
import sys, os, logging
from logging.handlers import RotatingFileHandler
from logging import Formatter

#from raven.contrib.flask import Sentry

# Set log variables
logdir = '/var/log/dmarc/'
error_log_file = 'error.log'
app_log_file = 'application.log'
log_level = 'DEBUG'

def define_handler():
	''' Set up the logging handlers '''
	
	""" 
		:Error Log:
		
		Error log handler has additional verbosity to identify the
		function and module reporting the event
	"""
	error_handler = RotatingFileHandler(
		'{0}{1}'.format(logdir,error_log_file), 
		maxBytes=10000000, 
		backupCount=9
	)
	
	error_handler.setFormatter(Formatter(
		'%(asctime)s %(name)s - %(levelname)s: %(message)s '
		'[in %(funcName)s %(pathname)s:%(lineno)d]')
	)
		
	errlog = logging.getLogger(__name__)
	errlog.setLevel(logging.getLevelName(logging.ERROR))
	errlog.addHandler(error_handler)

	"""
		: Application Log :
		
		Application log has less verbose output
	"""
	dmarc_handler = RotatingFileHandler(
		'{0}{1}'.format(logdir,app_log_file), 
		maxBytes=10000000, 
		backupCount=9
	)

	dmarc_handler.setFormatter(Formatter(
		'%(asctime)s %(levelname)s: %(message)s')
	)

	applog = logging.getLogger(__name__)
	applog.setLevel(logging.getLevelName(log_level))
	applog.addHandler(dmarc_handler)
	
	return applog, errlog

"""
	: Validate Log Path :
	
	Check if log directory exists, is writable, and if the log files exist and
	are writable. 
"""
if not logdir:
    dprint('Logging configuration missing. Exiting')
    sys.exit(1) 

if os.path.exists(logdir) and os.access('{0}{1}'.format(logdir,app_log_file), os.W_OK):
    applog, errlog = define_handler()
        
elif os.path.exists(logdir) and os.access(logdir, os.W_OK):
	applog, errlog = define_handler()

elif not os.path.exists(logdir):
	try:
		os.mkdir(logdir)
		applog, errlog = define_handler()
		
	except OSError:
		print('Failed creating log directory {0}. Exiting.'.format(logdir))
		sys.exit(1)

else:
    print('Cannot write to log files in {0}\nPath Exists: {1}\nDirectory is writable: {2}'.format(
        logdir, 
        os.path.exists(logdir), 
        os.access('{0}{1}'.format(logdir,app_log_file), os.W_OK)
        )
    )
    
    sys.exit(1)