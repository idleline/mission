import os, datetime, uuid, sys, re, ipaddress, time, requests
from ipwhois import IPWhois

from dmarc.lib.models import *

try:
    from .models import *
except Exception:
    from lib.models import *

def build_ip_dict():
    
    ip_dict = {}
    
    for ip in IPAddress.query.all():
        ip_dict[ip.address] = ip
        
    return ip_dict

def build_unmapped_ip_dict():
    
    ip_dict = {}
    
    for ip in db_session.query(IPAddress).filter(IPAddress.network_id == 0).all():
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

def build_network_dict():
    
    network_dict = {}
    
    for n in Network.query.all():
        network_dict[n.cidr] = n
        
    return network_dict

def build_update_nets():
    
    network_dict = {}
    
    for n in Network.query.all():
        network_dict[n] = []
        
    return network_dict

def build_asn_dict():
    
    asn_dict = {}
    
    for a in ASN.query.all():
        asn_dict[a.asn] = a
        
    return asn_dict

def get_org_from_ripe_net(net):
    #get_org_from_ripe_net('85.158.142.0/24')
    base_url = 'https://rest.db.ripe.net/search.json?query-string='
    qs = net
    source = '&source=RIPE'
    flags = '&flags=no-irt'
    full_url = base_url + qs + source + flags
    headers = {'Accept' : 'application/json'}
    r = requests.get(url = full_url, headers = headers)
    jdata = r.json()
    for jd in jdata['objects']['object']:
        for attrs in jd['attributes']['attribute']:
            if attrs['name'] == 'organisation':
                org = attrs['value']
    return org

def get_asn_from_net(net):
    base_url = 'http://whois.arin.net/rest'
    nets_url = '/cidr/{0}'.format(net)
    full_url = base_url + nets_url
    headers = {'Accept' : 'application/json'}
    r = requests.get(url = full_url, headers = headers)
    return r

def get_asn_nets(org):
    
    base_url = 'http://whois.arin.net/rest'
    nets_url = '/org/{0}/nets'.format(org)
    
    full_url = base_url + nets_url
    
    headers = {'Accept' : 'application/json'}
    
    r = requests.get(url = full_url, headers = headers)
    
    jdata = r.json()
    nets = jdata['nets']['netRef']

    all_nets = []
    for n in nets:
        sa = ipaddress.ip_address(n['@startAddress'])
        ea = ipaddress.ip_address(n['@endAddress'])
        for summ_net in ipaddress.summarize_address_range(sa, ea):
            all_nets.append(summ_net)
    
def get_org_info(asn, detail = False):
    base_url = 'http://whois.arin.net/rest'
    asn_url = '/asn/{0}'.format(asn)
    full_url = base_url + asn_url
    headers = {'Accept' : 'application/json'}
    r = requests.get(url = full_url, headers = headers)
    jdata = r.json()
    if detail is True:
        return jdata
    else:
        org_ref = jdata['asn']['orgRef']['@handle']
        return org_ref


def populate_handle(asn):
    ''' Expects a SQLAlchemy Object '''
    asn.handle = get_org_info(asn.asn)

def bulk_handle_update():
    asns = ASN.query.filter(ASNS.handle == None).all()
    for a in asns:
        populate_handle(a)
        time.sleep(2)
        db_session.commit()

def map_addresses():

    update_nets = build_update_nets()    
    ips = build_unmapped_ip_dict()
    network_dict = build_network_dict()
    asn_dict = build_asn_dict()
    percentage = 0
    #asn_info = {}
    #cidr_blocks = {}

    '''
        : IP OBJECTS :
        
        {network_dict}      "Network" DB objects    <cidr>  : <sql obj>
        {asn_dict}          "ASN" DB objects        <asn>   : <sql obj> 
        {ips}               "IPAddress" DB objects  <ip>    : <sql obj>
        
            [ip]            String of IP Address
            {ip_addr_obj}   ipaddress module ip_address CLASS

            [net]           String of Network CIDR
            {net_cidr_obj}  ipaddress module ip_network CLASS 

    '''
    obj_count = len(ips.keys())
    print('Objects to process is {0}'.format(obj_count))
    count = 0
    for ip, ip_obj in ips.items():
        count += 1

        ip_addr_obj = ipaddress.ip_address(ip)
        
        found = False
        
        for net, net_obj in network_dict.items():
        
            net_cidr_obj = ipaddress.ip_network(net)

            if ip_addr_obj in net_cidr_obj:
                #net_obj.ips.append(ip_obj)
                update_nets[net_obj].append(ip_obj)
                asn = net_obj.asn.asn
                found = True
            
        '''        
        if found is False:
            time.sleep(2)
            print('Network for {0} not found'.format(ip))
            whois_object = IPWhois(ip_obj.address)
            wd = whois_object.lookup_rdap()
            asn = int(wd['asn'])
            cidr = wd['asn_cidr']
            desc = wd['asn_description']

            new_net = Network(cidr = cidr)
            new_net.ips.append(ip_obj)
            db_session.add(new_net)
            network_dict[cidr] = new_net
            
            if asn not in asn_dict.keys():
                new_asn = ASN(asn = asn, description = desc)
                new_asn.networks.append(new_net)

                db_session.add(new_asn)
                db_session.commit()
                
                asn_dict[asn] = new_asn
                
                print('Added ASN {0} - {1}'.format(asn, desc))

            else:
                asn_dict[asn].networks.append(new_net)
                db_session.commit()
                
                print('Added {0} to ASN {1}'.format(cidr, asn))
        '''

        ratio = int(100 * (count / obj_count))

        if ratio % 5 == 0 and percentage != ratio:
            percentage = ratio
            print('[{0}%] Complete'.format(ratio))

    tot_nets = len(update_nets.keys())
    print("Updating {0} networks".format(tot_nets))

    for net, iplist in update_nets.items():
        net.ips.extend(iplist)
        
    db_session.commit()

def rollback_objects():
    
    for a in Network.query.all():
        db_session.delete(a)
        
    for a in ASN.query.all():
        db_sesssion.delete(a)
    
    db_session.commit()


# from dmarc.lib.iplookup import map_addresses, rollback_objects
