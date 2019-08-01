'''
    
    dmarc.lib.utils
    
'''
# System Level imports
import requests, json, re, datetime, pytz, math
from collections import OrderedDict
from datetime import datetime

# Flask imports
from flask import request, session, redirect, url_for, render_template, flash, jsonify, send_from_directory, make_response

# SQLAlchemy import
from sqlalchemy import func, desc, distinct
from sqlalchemy.ext.declarative.api import DeclarativeMeta

# Application Level Imports
from dmarc import dprint
from dmarc.lib import models
from dmarc.lib.database import db_session, init_db
from dmarc.lib.models import *

# BS4 Import & Fallback
try:
    from bs4 import BeautifulSoup as xmlparse
except ImportError:
    from BeautifulSoup import BeautifulSoup as xmlparse

# CONSTANT
startDate = '2018-10-02'

def domain_nav():
    
    menu_items = '' 

    for d in Domain.query.all():  
        menu_items = menu_items + "<li><a href='/domain/{0}'>@{0}</a></li>".format(d.name)
    
    return menu_items


def ajax_response(status='success', data=None):
    ''' Global AJAX handler '''
    
    update_user_activity()
    
    return make_response(jsonify(
        status = status, 
        data = data,
        ), 200)

def update_user_activity():
    ''' Global timestamp to update user last user activity ''' 

    user = curr_user()
    profile = UserProfile.query.filter(UserProfile.user == user).first()
    profile.last_active = datetime.now()
    db_session.commit()

def epoch_to_datetime(epoch):
    ''' Convert an epoch timestamp to a timezone '''
    
    dt = datetime.utcfromtimestamp(epoch)
    dt = dt.replace(tzinfo=pytz.utc)

    return dt

def get_reports():
    ''' Return a list of all reports '''
        
    reports = []

    for r in DMARCReport.query.all():
        
        record_count = 0
        for rec in r.records:
            record_count += rec.count
        
        reports.append({
            'org'   : r.org.name,
            'count' : len(r.records),
            'start' : epoch_to_datetime(r.report_date_start),
            'end' : epoch_to_datetime(r.report_date_end), 
            'info' : r,
            'records': record_count,
            }
        )

    return reports

def get_org_reports():
    
    org_reports = {}
    
    orgs = DMARCOrg.query.all()
    
    for o in orgs:
        reports = o.reports

        mail_count = 0
        for r in reports:
            record_count = len(r.records)
            for rec in r.records:
                mail_count = mail_count + rec.count
        
        org_reports[o.name] = {
            'record_count' : record_count,
            'mail_count' : mail_count
        }
    
    return org_reports

def get_mta_report(mta):
    ''' Receiving MTA Report Data '''
    
    org = DMARCOrg.query.filter(DMARCOrg.name == mta).first()
    
    if org:
        reports = DMARCReport.query.filter(DMARCReport.org == org).all()
    
        for r in reports:
            r.report_date_start = epoch_to_datetime(r.report_date_start)
            r.report_date_end = epoch_to_datetime(r.report_date_end)
        
    else:
        reports = None
        
    return reports

def get_domain_detail(domain):
    
    domain = Domain.query.filter(Domain.name==domain).first()
    
    if not domain:
        return None
        
    domain.records = DMARCRecord.query.filter(DMARCRecord.id_header_from == domain).all()
    
    return domain

'''
    : API Functions :
'''
def api_get_report_id(request):
    
    data = {}
    
    report_id = request.json['report_id']
    draw = request.json['draw']
    length = int(request.json['length'])
    start = int(request.json['start'])
    end = start + length
    
    report = DMARCReport.query.filter(DMARCReport.report_id == report_id).first()
    if report is None:
    
        return make_response(jsonify(
        status = 'error', 
        ), 500)

    records = report.records
    
    rows = []
        
    for rec in records[start:end]:
        rows.append({
            'header'    : rec.id_header_from.name,
            'ip'        : rec.source_ip.address,
            'count'     : rec.count,
            'disp'      : rec.policy_disposition,
            'dkim'      : rec.policy_dkim,
            'spf'       : rec.policy_spf,
        })
    
    recordsTotal = len(records)
    recordsFiltered = len(records)
    
    return make_response(jsonify(
        {
            'draw'              : draw, 
            'recordsTotal'      : recordsTotal,
            'recordsFiltered'   : recordsFiltered,
            'data'              : rows,
            }
        ), 200)

def api_get_selectors_chart(q):
    
    data = {
            'labels' : [],
            'count'  : []
        }
    
    '''
        : DKIM Related data :
        
        {rec}   Records associated
        {ips}   IPS associated
        
        [id_header_from_id]     When set to 1 this is the paypal.com domain
        [policy_dkim]           Set to if DKIM passes or fails
        
        
    '''
    if q == 'rec':
    
        pq = db_session.query(DMARCRecord.selector_id, func.count(DMARCRecord.selector_id).\
            label('count')).\
            filter(DMARCRecord.selector_id != None).\
            filter(DMARCRecord.id_header_from_id == 1).\
            filter(DMARCRecord.policy_dkim == 'pass').\
            group_by(DMARCRecord.selector_id).\
            order_by(desc('count')).\
            limit(7)

    if q == 'ips':
        pq = Selector.query.join(DMARCRecord).\
            filter(DMARCRecord.id_header_from_id == 1).\
            filter(DMARCRecord.policy_dkim == 'pass').\
            with_entities(DMARCRecord.selector_id, func.count(distinct(DMARCRecord.source_ip_id)).\
            label('count')).\
            group_by(DMARCRecord.selector_id).\
            order_by(desc('count')).\
            limit(7)

    for sel in pq.all():
        selector = Selector.query.filter(Selector.id == sel[0]).first()
        data['labels'].append(selector.name)
        data['count'].append(sel[1])
                        
        '''
        pq = db_session.query(Selector, func.count(selector_ip_table.c.ip_id).label('count')).\
                filter(DMARCRecord.selector_id != None).\
                filter(DMARCRecord.id_header_from_id == 1).\
                filter(DMARCRecord.policy_dkim == 'pass').\
                join(selector_ip_table).\
                group_by(Selector).\
                order_by(desc('count')).\
                limit(7)
        
        for r in pq.all():
            data['labels'].append(r[0].name)
            data['count'].append(r[1])
        '''
    
    return make_response(jsonify(
        status = 'success', 
        data = data
        ), 200)

def api_get_headerfrom_chart():
    
    data = {
        'labels' : [],
        'count'  : []
    }
        
    hf_tuple_list = DMARCRecord.query.\
        filter(DMARCRecord.policy_disposition == 'none').\
        with_entities(DMARCRecord.id_header_from_id, func.count(DMARCRecord.id_header_from_id)).\
        group_by(DMARCRecord.id_header_from_id).\
        limit(6).\
        all()
    
    for hft in hf_tuple_list[1:]:
        domain = Domain.query.filter(Domain.id == hft[0]).first()
        data['labels'].append(domain.name)
        data['count'].append(hft[1])
    
    return make_response(jsonify(
        status = 'success', 
        data = data
        ), 200)
        
def api_get_spffail_domain():
    domains = {}    
    data = {
        'labels': [],
        'results' : {
            'fail'  : [],
            'pass'  : []
        }
    }

    for key in ['fail', 'pass']:
        spf_tuple = dmarc_policy_spf_sql(key)

        for spf in spf_tuple[1:]:
            domain = Domain.query.filter(Domain.id == spf[0]).first()

            if domain.name not in domains.keys():
                domains[domain.name] = {}
            domains[domain.name][key] = spf[1]


    for dom, res in domains.items():

        data['labels'].append(dom)    

        for pf in ['fail', 'pass']:
            if pf in domains[dom].keys():
                data['results'][pf].append(domains[dom][pf])
            else:
                data['results'][pf].append(0)

    return make_response(jsonify(
        status = 'success', 
        data = data
        ), 200)
        
def dmarc_policy_spf_sql(key):         

    spf_tuple = DMARCRecord.query.\
        filter(DMARCRecord.policy_spf == key).\
        with_entities(DMARCRecord.id_header_from_id, func.count(DMARCRecord.id_header_from_id)).\
        group_by(DMARCRecord.id_header_from_id).\
        limit(6).\
        all()

    return spf_tuple

def api_get_ip_usage():
    
    data = {
        'labels' : [],
        'count'  : []
    }
    
    ip_tuple = DMARCRecord.query.\
        filter(DMARCRecord.id_header_from_id == 1).\
        filter(DMARCRecord.policy_disposition == 'none').\
        with_entities(DMARCRecord.source_ip_id, func.count(DMARCRecord.source_ip_id).label('count')).\
        group_by(DMARCRecord.source_ip_id).\
        order_by(desc('count')).\
        limit(10)    

    for ip_id, count in ip_tuple: 
        ip_addr = IPAddress.query.filter(IPAddress.id == ip_id).first()
        
        data['labels'].append(ip_addr.address)
        data['count'].append(count)
        
    return make_response(jsonify(
        status = 'success', 
        data = data
        ), 200)

def get_dashboard_ips():
    ''' For PayPal.com IPs only '''
    
    ips = IPAddress.query.\
        join(DMARCRecord).\
        filter(DMARCRecord.source_ip_id == IPAddress.id).\
        filter(DMARCRecord.policy_disposition == 'none').\
        filter(DMARCRecord.id_header_from_id == 1).\
        all()
    
    return ips
            
'''
    : Full Table Queries :
'''

def get_dmarc_orgs():

    return DMARCOrg.query.all()

def get_all_records():
    
    return DMARCRecord.query.all()
    
def get_all_ips():
    
    return IPAddress.query.all()

def get_all_reports():
        
    return DMARCReport.query.all()

def get_all_selectors():
    
    return Selector.query.all()

def get_all_domains():
    
    return Domain.query.all()