#!/usr/bin/env python3
import os, datetime, uuid, sys, re
from bs4 import BeautifulSoup

try:
    from .models import *
except Exception:
    from lib.models import *

def read_files():
    ''' Look for RUA files '''
    
    count = 0
    rua_files = []
    
    for root, dirs, files in os.walk("./data", topdown=False):
        for name in files:
            if name == 'data':
                rua_files.append(os.path.join(root, name))
                count += 1
    
    print('[{0}] Found {1} RUA files\n'.format(dt_now(),count))

    return rua_files

'''
    : BUILD DICTIONARIES :
    
    For DB Objects
'''

def build_ip_dict():
    
    ip_dict = {}
    
    for ip in IPAddress.query.all():
        ip_dict[ip.address] = ip
        
    return ip_dict
    
def build_header_dict():
    
    header_dict = {}
    
    for hf in Domain.query.all():
        header_dict[hf.name] = hf
        
    return header_dict
    
def build_selector_dict():
    
    selector_dict = {}
    
    for s in Selector.query.all():
        selector_dict[s.name] = s
        
    return selector_dict
    
def build_domain_dict():
    
    domain_dict = {}
    
    for d in Domain.query.all():
        domain_dict[d.name] = d
        
    return domain_dict
    
'''
    : SUPPORT FUNCTIONS :
    
'''
def find_pp_selector(r):

    s_tags = r.findAll('selector')
    
    for tag in s_tags:
        if re.match('[a-z0-9]*\.?paypal\.com', tag.find_previous_siblings('domain')[0].string):
            
            return tag.string
    
    return None

'''
    : MAIN FUNCTIONS :
    
    Main parsing function for iterating through the XML data from RUA
    files provided by mail providers
'''

def parse_data(filename):
    ''' Parse an RUA file to return useful data '''
    
    print('[{0}] Parsing file: {1}'.format(dt_now(), filename))

    with open(filename, 'r') as fo: 
        soup = BeautifulSoup(fo.read(), 'lxml')

        print('[{0}] Finished parsing file - Looking for records'.format(dt_now()))

    ''' 
        : PARSE REPORT DATA :
    
        Getting report metadata
    '''
    policy_domain = soup.feedback.policy_published.domain.text
    records = soup.feedback.findAll('record')
    
    print('[{0}] Found {1} records'.format(dt_now(), len(records))) 

    # DOMAIN LOOKUP
    domain = Domain.query.filter(Domain.name == policy_domain).first()            
    if domain is None:
        domain = Domain(name = policy_domain)
        db_session.add(domain)
        db_session.commit()
    
    # ORG LOOKUP
    org_name = soup.feedback.report_metadata.org_name.text    
    org = DMARCOrg.query.filter(DMARCOrg.name == org_name).first()
    
    if org is None:
        org = DMARCOrg(name = org_name)
        db_session.add(org)
        db_session.commit()
    
        #org = DMARCOrg.query.filter(DMARCOrg.name == org_name).first()
    
    # REPORT ID LOOKUP - ADD
    rep_id = soup.feedback.report_metadata.report_id.text
                
    if DMARCReport.query.filter(DMARCReport.report_id == rep_id).first() is None:
    
        report = DMARCReport(
            org = org,
            report_id = rep_id,
            report_date_start = int(soup.feedback.report_metadata.date_range.begin.text),
            report_date_end = int(soup.feedback.report_metadata.date_range.end.text),
            policy_domain = domain,
        )

        db_session.add(report)
        db_session.commit()
          
    report = DMARCReport.query.filter(DMARCReport.report_id == rep_id).first()
    domain = Domain.query.filter(Domain.name == policy_domain).first()

    fo.close()
    
    '''
        : HEADER DOMAINS :
        
        Add all new domains found in header from
    '''    
    domain_dict = build_domain_dict()
    new_domains = []

    header_from_tags = soup.findAll('header_from')
    
    for hf_tag in header_from_tags:
        if hf_tag.string not in domain_dict.keys():
    
            domain = Domain(name = hf_tag.string)
            new_domains.append(domain)
            domain_dict[domain.name] = domain
    
    if len(new_domains) > 0:
        db_session.bulk_save_objects(new_domains)
        db_session.commit()
    
    ''' 
        : SOURCE IP :
    
        Add all source IPs to DB if not already in it
        
    '''
    ip_dict = build_ip_dict()
    
    source_ip_tags = soup.findAll('source_ip')
    
    db_ip_objs = []
    
    for src_ip in source_ip_tags:
        if src_ip.string not in ip_dict.keys():
        
            ip_addr = IPAddress(
                address = src_ip.string
                )
        
            db_ip_objs.append(ip_addr)
        
        else: 
            ip_addr = ip_dict[src_ip.string]

        ip_dict[ip_addr.address] = ip_addr
    
    print("[{0}] Adding {1} IPs to database".format(dt_now(), len(db_ip_objs)))
    
    if len(db_ip_objs) > 0:
        db_session.bulk_save_objects(db_ip_objs)
        db_session.commit()
    
    '''
        : SELECTORS:
        
        Add all selectors found in the report
    '''
    selector_dict = build_selector_dict()
    new_selectors = []
     
    selectors = soup.findAll('selector')
    
    print('[{0}] Found {1} selectors'.format(dt_now(), len(set(selectors))))
    
    for s in selectors:        
        pp_domain = re.match('[a-z0-9]*\.?paypal\.com', s.find_previous_siblings('domain')[0].string)
        
        if pp_domain and s.string not in selector_dict.keys():
            
            selector_object = Selector(
                name = s.string
            )
            
            selector_dict[selector_object.name] = selector_object
            
            new_selectors.append(selector_object)
            
    print("[{0}] Adding {1} selectors to database".format(dt_now(), len(new_selectors)))            
    
    if len(new_selectors) > 0: 
        db_session.bulk_save_objects(new_selectors)
        db_session.commit()
    
    for s in selectors:
        pp_domain = re.match('[a-z0-9]*\.?paypal\.com', s.find_previous_siblings('domain')[0].string)

        if pp_domain and s.string not in domain_dict[pp_domain.group()].selectors:
            domain_dict[pp_domain.group()].selectors.append(selector_dict[s.string])
        
    db_session.commit()
    
    '''
        : PARSE RECORDS :
        
        Find all records and add them to the database
    '''
    
    db_rec_objs = []
    err_count = 0
      
    print("[{0}] Starting to parse {1} records".format(dt_now(), len(records)))
    record_start = datetime.datetime.now()
    total_count = 0
    periodic_alert = 5000
    
    ip_dict = build_ip_dict()
    selector_dict = build_selector_dict()
    domain_dict = build_domain_dict()
    
    for r in records:
        
        ip_text = r.row.source_ip.string
        
        total_count += 1
    
        ip_addr = ip_dict[ip_text]
        id_header_from = domain_dict[r.identifiers.header_from.text]

        policy_disposition = r.row.policy_evaluated.disposition.text
        
        #selector_tag = r.find('selector')
        selector_tag = find_pp_selector(r)
        
        if selector_tag:
            selector = selector_dict[selector_tag.string]
        
            if ip_addr.address not in selector.ips:
                selector.ips.append(ip_addr)
            
        else:
            selector = None
                        
        if id_header_from not in ip_addr.domains:
            ip_addr.domains.append(id_header_from)
                
        if report is not None:
            rec = DMARCRecord(
                guid = uuid.uuid5(uuid.NAMESPACE_DNS, str(r)),
                report = report,
                count = int(r.row.count.text),
                policy_disposition = policy_disposition,
                policy_dkim = r.row.policy_evaluated.dkim.text,
                policy_spf = r.row.policy_evaluated.spf.text,
                id_header_from = id_header_from,
                source_ip = ip_addr,
            )
            
            if selector:
                rec.selector = selector

            db_rec_objs.append(rec)
            
            if total_count % periodic_alert == 0:
                print('[{0}] Status: {1} records of {2} reviewed'.format(dt_now(), total_count, len(records)))
    
    total = format_time(datetime.datetime.now() - record_start)
    print('[{0}] Completed parsing {1} in {2}\nStarting to bulk commit {2} records to DB'.format(dt_now(), len(db_rec_objs), total_count))                                             
    db_session.bulk_save_objects(db_rec_objs)
    db_session.commit()
    
    print('[{0}] Finished bulk commit'.format(dt_now()))

def dt_now():
    
    return datetime.datetime.now().strftime('%H:%M:%S')


def format_time(delta):
    
    if delta.seconds > 60:
    
        minutes = int(delta.total_seconds() / 60)
        seconds = int(delta.total_seconds() % 60)        
        
        total = "0:{0}:{1}".format(minutes, seconds)
        
    else:
        minutes = 0
        seconds = delta.seconds
        
        total = "0:0:{0}".format(delta.seconds)
    return total

if __name__ == '__main__':
    ''' Main Function '''
    
    start = datetime.datetime.now()
    
    print('[{0}] Script started\n'.format(dt_now()))

    for f in read_files(): 
        parse_data(f)
    
    total = format_time(datetime.datetime.now() - start)
    
    print('[{0}] Script took {1} to complete'.format(dt_now(), total))

    
