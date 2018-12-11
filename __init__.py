# -*- coding: latin-1 -*-
'''
    
    mission 
    
    Mission House Home Automation App to display information about our house. 
    
'''
# System level import functions
from __future__ import print_function
import sys, logging

def dprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Flask application and plugin dependencie
import flask_babel as babel
from flask import Flask, render_template
from raven.contrib.flask import Sentry
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap
from flask_security import Security, SQLAlchemyUserDatastore
from flask_assets import Bundle, Environment
from flask_sqlalchemy import SQLAlchemy

# Application level imports
from mission.lib.assets import bundles

def format_datetime(value, format='medium'):
    if format == 'full':
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE MM/dd y HH:mm"

    return babel.dates.format_datetime(value, format)

def format_date(value, format='medium'):
    if format == 'full':
        format="EEEE, d MMMM y"
    elif format == 'medium':
        format="EE MM/dd y"

    return babel.dates.format_datetime(value, format)

# Initialize the Flask application
app = Flask(__name__)

# Because we're security-conscious developers, we also hard-code disabling
# the CDN support (this might become a default in later versions):
app.config.from_object('config')

# Install our Bootstrap extension
Bootstrap(app)

# Initialize Asset Bundles 
assets = Environment(app)
assets.register(bundles)

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['date'] = format_date
#security = Security(app, user_datastore)

from .views import dashboard
app.register_blueprint(dashboard)

'''
    Initialize all Blueprints 
    
    @param {mod_auth}       Authentication module for user datastore manipulation
    @param {admin}          Application administration
    @param {tattletale}     Tattletale DNS Blacklist application
    @param {wildrice}       WildFire IoC Maltego transforms
    @param {ipmol}          IP Blacklist for PAN Firewalls EBL service

    @param {untrust}        unTrust - The underlying application framework
    

# Authentication Blueprint
from unTrust.mod_auth.controllers import mod_auth as auth_module
app.register_blueprint(auth_module)

# Admin Blueprint
from unTrust.admin.views import app_admin
app.register_blueprint(app_admin, url_prefix='/admin')

# Initialize Jinja Date formatters
app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['date'] = format_date

    :: Sentry ::
    
    Application error reporting 
    
    @func [bad_request]             Bad request
    @func [build_error]             Template issues
    @func [page_not_fount]          404 Page handling
    @func [sql_error]               SQL database error
    @func [internal_server_error]   Internal Server Error

# Exception registration imports
import werkzeug.exceptions, werkzeug.routing, sqlalchemy.exc, jinja2.exceptions, flask_nav

# Sentry definition for error reporting
sentry = Sentry(app, logging=True, level=logging.ERROR, dsn='https://c4f24453ecd440218ff623a0f49d5596:5fdbf0c50cee4f88ad77cef4762a144e@app.getsentry.com/91255')

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

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return render_template('error.html', msg=e)
    
@app.errorhandler(werkzeug.exceptions.BadRequest)
def bad_request(e):
    return render_template('error.html', msg=e)
    
@app.errorhandler(werkzeug.routing.BuildError)
def build_error(e):
    return render_template('error.html', msg=e)
    
@app.errorhandler(sqlalchemy.exc.OperationalError)
def sql_error(e):
    return render_template('error.html', msg=e)

@app.errorhandler(flask_nav.NavbarRenderingError)
def navbar_render_error(e):
    return render_template('error.html', msg=e)
'''