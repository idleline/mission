import os, datetime, uuid, sys, re, ipaddress, 
from ipwhois import IPWhois

try:
    from .models import *
except Exception:
    from lib.models import *

def parse_ipam(data):
    regex = '(?<="network": ")[^"]+'
    
    routes = re.findall(regex, data)
    
    return routes

def number_fields(file, delimeter):
    with open(file, 'r') as fo:
        lines = fo.readlines()
    
    headers = lines[0].split(delimeter)

def summarize(routes):
    nets = []
    for n in ipaddress.collapse_addresses(routes):
        nets.append(n)
    return nets

ips = IPAddress.query.all()
asn_info = {}
cidr_blocks = {}
for ip in ips:
    ip_obj = ipaddress.ip_address(ip.address)
    found = False
    for net, asn in cidr_blocks.items():
        if ip_obj in net:
            asn_info[asn]['ips'].append(ip.address)
            found = True
            print('Found', ip.address, asn)
    if found is False:
        print('Not Found')
        whois_object = IPWhois(ip.address)
        wd = whois_object.lookup_rdap()
        asn = wd['asn']
        cidr = wd['asn_cidr']
        desc = wd['asn_description']
        if asn not in asn_info.keys():
            asn_info[asn] = {
            'cidr' : [cidr],
            'description' : desc,
            'ips' : [ip.address],
            }
        else:
            asn_info[asn]['cidr'].append(cidr)        
        cidr_blocks[ipaddress.ip_network(cidr)] = asn

for k,v in asn_info.items():
    asn_info[k]['count'] = len(v['ips'])
    mylist.append()
    print(len(v['ips'], k, v['description']))
    


    
        
    


if __name__ == '__main__':

    ips = IPAddress.query.all()    

    ip_list = []

    for ip in ips:
        ip_list.append(ipaddress.ip_network(ip))
    
    nets = summarize(ip_list)
    
    print('{0} )

    
    '''
    parser = argparse.ArgumentParser(description='Summarize routes from file data')
    parser.add_argument('-p', '--parse', action='store_true', dest='parse', help='Parse IPAM file output')
    parser.add_argument('-i', '--in', action='store', dest='infile', required=True, help='Input file for routes in IPAM or newline separated format')
    parser.add_argument('-o', '--out', action='store', dest='outfile', required=True, help='Output file to put summary data into')
    
    args = parser.parse_args()
    
    if args.parse is True:
        with open(args.infile, 'r') as infile: 
            data = parse_ipam(infile.read())
    else:
        with open(args.infile, 'r') as infile:
            data = infile.readlines()
            
    for i in range(len(data)):
        data[i] = ipaddress.ip_network(data[i].strip())

    outfile = open(args.outfile, 'w')
    
    nets = summarize(data)
    for net in nets:
        outfile.write("{0}\n".format(str(net)))
    
    outfile.close()
    
    print("Summarized {0} into {1} routes".format(len(data), len(nets)))
    '''