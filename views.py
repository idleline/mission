'''
   
    dmarc.views
    
'''
# System level imports
import os, sys, sqlite3, json
from dmarc.lib.utils import *
from dmarc import dprint

# Flask dependencies
from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, current_app
from flask_mail import Message
from jinja2.exceptions import TemplateNotFound

dashboard = Blueprint('dashboard', __name__)

'''
    : Default View Handlers :
    
    For general access requests used by most all Flask apps I build
    
    Static file handers and the default page
'''
@dashboard.add_app_template_global
def get_domain_nav(caller=None):
    
    return domain_nav()

@dashboard.route('/', defaults={'page': 'index'})
@dashboard.route('/<page>')
def show(page):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        return render_template('error.html', msg='404: Page Not Found')

@dashboard.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(dashboard.root_path, 'static/icons'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

@dashboard.route('/icons/<string:icon>')
def icons(icon):
    ''' Icon Handler '''

    return send_from_directory(os.path.join(dashboard.root_path, 'static/icons/'), icon)
    
@dashboard.route('/assets/<string:asset>')
def assets(asset):
    ''' Asset Handler '''

    return send_from_directory(os.path.join(dashboard.root_path, 'assets/'), asset)
    
@dashboard.route('/fonts/<string:font>')
def fonts(font):
    ''' Font Handler '''

    return send_from_directory(os.path.join(dashboard.root_path, 'static/fonts/'), font)

@dashboard.route('/')
def index():
    ''' Main Page Handler (INDEX)'''
        
    return dashboard_viewer()
    
@dashboard.route('/dashboard')
def dashboard_viewer():
    ''' Dashboard View '''
    
    return render_template('dashboard.html', 
        orgs = get_dmarc_orgs(), 
        records = get_all_records(), 
        ips = get_dashboard_ips(), 
        reports = get_all_reports(),
        selectors = get_all_selectors(),
        domains = get_all_domains(),
        )

@dashboard.route('/reports')
def mta_report_summary():
    ''' Report Detail View '''

    return render_template('reports.html', 
        orgs = get_dmarc_orgs(),
        org_reports = get_org_reports()
    )

@dashboard.route('/reports/<string:mta>')
def mta_reports(mta):
    ''' Report Detail View '''

    return render_template('reports.html', 
        reports = get_mta_report(mta),
        orgs = get_dmarc_orgs(),
        org_reports = get_org_reports()
    )

@dashboard.route('/domain/<string:domain>')
def domain_detail(domain):
    ''' Domain Detail View '''

    return render_template('domain.html', domain = get_domain_detail(domain))

'''
    : AJAX Calls :
    
    From javascript assets
    
'''
@dashboard.route('/api/report_id', methods=['POST'])
def api_report_id():
    
    return api_get_report_id(request)

@dashboard.route('/api/selectors/chart')
def api_selectors():
    
    return api_get_selectors_chart('rec')

@dashboard.route('/api/selectorips/chart')
def api_selector_ips():
    
    return api_get_selectors_chart('ips')

@dashboard.route('/api/headerfrom/chart')
def api_headerfrom_chart():    
    
    return api_get_headerfrom_chart()

@dashboard.route('/api/spffail/chart')
def api_spffail_domain():
    
    return api_get_spffail_domain()

@dashboard.route('/api/topips/chart')
def api_topips_chart():

    return api_get_ip_usage()

@dashboard.route('/login')
def login():
    ''' Main Page Handler '''
        
    return render_template('auth.html')