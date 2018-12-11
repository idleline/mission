'''
   
    mission.views
    
'''
# System level imports
import os, sys, sqlite3, json
from mission.lib.utils import *
from mission import dprint

# Flask dependencies
from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, current_app
from flask_bootstrap import Bootstrap
from flask_security import login_required, roles_required, SQLAlchemyUserDatastore, current_user
from flask_mail import Message
from jinja2.exceptions import TemplateNotFound

dashboard = Blueprint('dashboard', __name__)


'''
    : Default View Handlers :
    
    For general access requests used by most all Flask apps I build
'''
@dashboard.route('/', defaults={'page': 'index'})
@dashboard.route('/<page>')
def show(page):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        return render_template('404.html')

@dashboard.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(dashboard.root_path, 'static/icons'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

@dashboard.route('/icons/<string:icon>')
def icons(icon):
    ''' Icon Handler '''

    return send_from_directory(os.path.join(dashboard.root_path, 'static/icons/'), icon)
    
@dashboard.route('/fonts/<string:font>')
def fonts(font):
    ''' Font Handler '''

    return send_from_directory(os.path.join(dashboard.root_path, 'static/fonts/'), font)

@dashboard.route('/')
def index():
    ''' Main Page Handler '''
        
    return render_template('mission.html', devices=mission_status(), cameras=camera_status(), cams=ring_cameras())    

"""
    : Example Views :

    Some examples used in the past

"""
"""
@dashboard.route('/activity', methods=['POST'])
def activity():
    ''' Return Map Activity '''

    hunter_activity = map_activity()
    icons = icon_activity()
    return json.dumps({ 'coords' : hunter_activity, 'icons' : icons })

@dashboard.route('/test', methods=['POST'])
def test_activity():
    ''' Return Test Map Data '''
    
    results = test_map_activity()
    return json.dumps({ 'coords' : results })

@dashboard.route('/add')
def add():
    ''' Return Add Form Page '''
    
    return render_template('add.html')

@dashboard.route('/api/add', methods=['POST'])
def api_add():
    
    response = add_marker(request)
    
    return json.dumps({'status' : 'ok'})

@dashboard.route('/api/deleteIcon')
def icon_delete():

    try:
        obj = request.args['obj']
        id = request.args['id']
    except Exception as err:
        return render_template('404.html')
    
    delete_icon(obj, id)
    
    return render_template('index.html', forecast=weather(), activity=get_activity())

"""