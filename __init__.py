# -*- coding: latin-1 -*-
'''
    
    dmarc 
    
    Web 2.0 framework for web apps
    
'''
# System level import functions
from __future__ import print_function
import sys, logging, re

"""
    : PRE-INITIALIZATION :
    
    Functions that need to be imported by children application modules should be here
    
    {dprint}        Debug printer for console error debugging
    {q}             Message queueing for crash reporting
"""
def dprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#q = Queue.Queue()
"""
    : APPLICATION INITIALIZATION :
    
    Rest of application load
"""

# Flask application and plugin dependencies
import flask_babel as babel
from flask import Flask, render_template, g
from raven.contrib.flask import Sentry
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap
from flask_security import Security, SQLAlchemyUserDatastore
from flask_assets import Bundle, Environment
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from jinja2 import evalcontextfilter, Markup, escape
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

# Python level imports
from dateutil.tz import gettz
from dateutil.parser import parse

# Application level imports
from dmarc.lib.assets import bundles, scss_bundles
# from dmarc.scheduling.jobs import *
from dmarc.lib.database import db_session, init_db

"""
    : MAIN APP :
    
    Initializing the main application from configuration & bootstrapping
"""

# Initialize the Flask application
app = Flask(__name__)

# Because we're security-conscious developers, we also hard-code disabling
# the CDN support (this might become a default in later versions):
app.config.from_object('config')


# Job Scheduler
"""
    : INITIALIZE SCHEDULER :
    
    Define functions for the job scheduler & init objects


def job_supervisor(event):
    while not q.empty():
        msg = 'Message from job {0} : {1}'.format(event.job_id, q.get())
        dprint(msg)
        applog.info(msg)
    
    if event.exception:
        errlog.warning('Job {1} Exception Code: {0}'.format(event.code, event.job_id))

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_listener(job_supervisor, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
scheduler.start()
"""


"""
    : JINJA DATE & TIME FORMAT :
    
    Date and Time formats for use in jinja HTML templates.
    
    Hard coded to ARIZONA TIMEZONE
"""

def format_datetime(value, format='full'):
    if isinstance(value, str):
        value = parse(value)
    
    if format == 'full':
        format = "EEEE, MMMM d 'at' hh:mm a"
    elif format == 'medium':
        format="EE MM/dd y HH:mm"

    return babel.dates.format_datetime(value, format, tzinfo=gettz('US/Arizona'))

def format_date(value, format='medium'):
    if format == 'full':
        format="EEEE, d MMMM y"
    elif format == 'medium':
        format="EE MM/dd y"

    return babel.dates.format_datetime(value, format) 

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['date'] = format_date

# Dashboard (Main) Blueprint
from .views import dashboard
app.register_blueprint(dashboard)


"""
    : SUPPORT PLUGINS : 
    
    @param {assets}             Static asset management (css & js)
    @func  {shutdown_session}   SQL connection handling
    
"""
# ASSET BUNDLES
#Scss(app)
assets = Environment(app)
assets.debug = True
assets.register(bundles)

# DATABASE SESSION MANAGEMENT
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

init_db()

'''
    :: Sentry ::
    
    Application error reporting 
    
    @func [bad_request]             Bad request
    @func [build_error]             Template issues
    @func [page_not_fount]          404 Page handling
    @func [sql_error]               SQL database error
    @func [internal_server_error]   Internal Server Error

# Sentry definition for error reporting
sentry = Sentry(app, logging=True, level=logging.ERROR, dsn='https://c4f24453ecd440218ff623a0f49d5596:5fdbf0c50cee4f88ad77cef4762a144e@app.getsentry.com/91255')
'''
# Exception registration imports
import werkzeug.exceptions, werkzeug.routing, sqlalchemy.exc, jinja2.exceptions

# Register error handlers
@app.errorhandler(404)
def page_not_found(e):

    return render_template('error.html', msg=e)

@app.errorhandler(405)
def method_not_allowed(e):

    return render_template('error.html', msg=e)

@app.errorhandler(500)
def internal_server_error(e):

    return render_template('error.html', msg=e)
    
@app.errorhandler(502)
def internal_server_error(e):

    return render_template('error.html', msg=e)

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):

    return render_template('error.html', msg=e)
    
@app.errorhandler(werkzeug.exceptions.BadRequest)
def bad_request(e):

    dprint(e, e.description, e.get_description(), e.message, e.name, e.response, e.code)
    return render_template('error.html', msg=e), 400
    
@app.errorhandler(werkzeug.routing.BuildError)
def build_error(e):

    return render_template('error.html', msg=e)
    
@app.errorhandler(sqlalchemy.exc.OperationalError)
def sql_error(e):

    return render_template('error.html', msg=e)