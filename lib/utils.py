'''
    
    swordpoint.lib.utils
    
'''
# System Level imports
import requests, json, re
from collections import OrderedDict
from datetime import datetime
from ring_doorbell import Ring

# SQLAlchemy import
from sqlalchemy.ext.declarative.api import DeclarativeMeta

# Application Level Imports
from swordpoint import dprint
from swordpoint.lib.database import db_session, init_db
from swordpoint.lib import models
from swordpoint.lib.models import *

# BS4 Import & Fallback
try:
    from bs4 import BeautifulSoup as xmlparse
except ImportError:
    from BeautifulSoup import BeautifulSoup as xmlparse

# CONSTANT
startDate = '2018-10-02'

init_db()

def mission_status():
    with open('device-status.txt', 'r') as fo:
        devices = json.loads(fo.read())
    
    return devices['devices']['thermostats']['JbkbAb8Veduy0TQA1LI8e5gQ-5OYfhvG']

def camera_status():
    
    with open('device-status.txt', 'r') as fo:
        devices = json.loads(fo.read())

    return devices['devices']['cameras']['5cjAyIjJJk65RCr2eWqwrPkWJKBPINEWXHmsMGRJsVCYEPuTmH4bxg']

def nest_read_thermostat(authZ):
    url = 'https://developer-api.nest.com'
    
    token = 'c.h3o91kPZhiPS04bd9tgCutv8LOMho7pzacRgVCKnUULeTOkMJBAFIHfaNuQlMnfa68J00XX2F0TkQsaDeMAVflzic2o8epG8smFuiMzQQlfARxt8TRtkLUgzJ4ObGYXBcrDvP80IeBGkr5it'

    headers = {
        'Authorization': "Bearer {0}".format(token),
        'Content-Type' : 'application/json'
    }   

    r = requests.get(url, headers=headers, verify=False, allow_redirects=False)
    
    if r.status_code == 307:
        resp = requests.get(r.headers['Location'], headers=headers, allow_redirects=False)
        
        status = json.loads(resp.text)
    
        return status
    
    return None

def ring_cameras():
    devices = get_ring_devices()
    
    cams = devices['stickup_cams']
    
    for c in cams:
        c.snapshot_url = c.recording_url(c.last_recording_id)
    
    return cams 


def get_ring_devices():
    user = 'lawheelock@gmail.com'
    pw = 'R%aZ00r4$'
    
    ring = Ring(user, pw)
    
    return ring.devices
    
    '''
    doorbell = ring.devices['doorbell'][0]
    doorbell.recording_download(
        doorbell.history(
            limit=100, 
            kind='ding')[0]['id'],
            filename='last_ding.mp4',
            override=True
        )
    '''
    
"""
    : Example Functions : 
"""
'''
def weather():
    """
        : Colorado Flat Tops :
    """
    lon = "-107.19720252801557"
    lat = "39.881855710363055"
    

    """
        : 4B East :
    """
    lat = "34.52239"
    lon = "-110.52853"
    
    """
        : 36A :     
    """
    lat = "31.789661044426566"
    lon = "-111.29362649777008"

    url = "http://forecast.weather.gov/MapClick.php?lon={0}&lat={1}&FcstType=dwml".format(lon, lat)
    r = requests.get(url)
    
    data = xmlparse(r.text, 'lxml')
    forecast = data.data

    days = []
    
    for d in data.find('time-layout').findAll(attrs={'period-name': re.compile(".*")})[0:6]:
        days.append(d.attrs['period-name'])
        
    forecast = []
    
    maxTemps = data.parameters.findAll(attrs={'type' : 'maximum'})[0].findAll('value')
    minTemps = data.parameters.findAll(attrs={'type' : 'minimum'})[0].findAll('value')
    icons = data.parameters.find('conditions-icon').findAll('icon-link')
    wordedForecast = data.parameters.wordedforecast.findAll('text')
    precip = data.parameters.find('probability-of-precipitation').findAll('value')
    
    dprint('Max', len(maxTemps), maxTemps, '\n', 
        'Min', len(minTemps), minTemps, '\n', 
        'Word', len(wordedForecast),  wordedForecast, '\n', 
        'Precip', len(precip), precip)

    for i in range(len(days)):
        if precip[i].text == '':
            precip_val = '0'
        else:
            precip_val = precip[i].text
        
        forecast.append({
            'name' : days[i],
            'max': maxTemps[i].text, 
            'min' : minTemps[i].text,
            'icon' : icons[i].text,
            'wordedForecast' : wordedForecast[i].text,
            'precip' : precip_val })
    
    return forecast

""""
    : Map Activity :
   
    Routines for identifying map activity of hunters and events sent to the API
        
"""
def get_activity():

        : Colorado Hunt Party :
        
    hunterList = [
        {'name': 'Ralph', 'feedId': 'RalphForsythe', 'auth': None},
        {'name': 'Lance', 'feedId': 'LaurenceWheelock', 'auth': None},
        {'name': 'Dustin', 'feedId': 'DustinRomney', 'auth': None},
        {'name': 'Mike', 'feedId': 'mbaird', 'auth': None}
    ]
    
    
    
        : Arizona 2018 Hunt Party :
    
    hunterList = [
        {'name': 'Lance', 'feedId': 'LaurenceWheelock', 'auth': None}, 
        {'name': 'Dustin', 'feedId': 'DustinRomney', 'auth': None}
    ]
    
    # Initialize Activity object to return to the AJAX call from map.js
    activity = []
    activity_dict = {}
    for hunter in hunterList:
        url = "https://share.delorme.com/feed/Share/{0}?d1={1}T07:00-700".format(hunter['feedId'], startDate)
        r = requests.get(url)

        data = xmlparse(r.text, 'lxml')
        try:
            placemarks = data.document.folder.findAll('placemark')
        
        except AttributeError, err:
            dprint(url)
            dprint('swordpoint.lib.utils.get_activity [placemarks]', hunter, err) # Print hunter & error
            placemarks = []
        
        for p in placemarks[:-1]:
            try:
                lat = float(p.find(attrs={'name':'Latitude'}).value.text)
                lon = float(p.find(attrs={'name':'Longitude'}).value.text)
                name = re.sub(r'ure', '', p.find(attrs={'name': 'Name'}).value.text.split(' ')[0])
                    
                entry = {
                    'name': name,
                    'time': p.find(attrs={'name':'Time'}).value.text,
                    'event' : p.find(attrs={'name':'Event'}).value.text,
                    'ele' : "{0} ft".format(
                        round(float(p.find(attrs={'name':'Elevation'}).value.text.split(' ')[0]) * 3.28084)),
                    'velocity' : u"{0} mph {1} \xb0".format(
                        round(float(p.find(attrs={'name':'Velocity'}).value.text.split(' ')[0]) * 0.621371), 
                        p.find(attrs={'name':'Course'}).value.text.split(' ')[0]), 
                    'lat' : lat,
                    'lon' : lon,
                }
                
                activity_dict[p.find(attrs={'name':'Time'}).value.text] = entry
            
            except Exception, err:
                dprint('swordpoint.lib.utils.get_activity [placemark iter]', err)
                pass
    
    if len(placemarks) < 1:
        activity = 0
    else:
        ordered = sorted(activity_dict.items(), key = lambda x:datetime.datetime.strptime(x[0], "%m/%d/%Y %I:%M:%S %p"), reverse=True)
        for e in ordered:
            activity.append(e[1])
    
    return activity

def map_activity():
     Using the Delorme sharing API find hunter activity 
    
    
        : Colorado 2016 Hunt Party :

    hunters = [
        {'mapShare': 'RalphForsythe', 'mapAuth': 'UmFscGhGb3JzeXRoZTpCaWdFbGs=', 'mapData': {
            'name' : 'Ralph', 'data':{'color': '#383636', 'colorName': 'black', 'points': [] } } },
        {'mapShare': 'LaurenceWheelock', 'mapAuth': None, 'mapData': {
            'name' : 'Lance', 'data':{'color': '#147516', 'colorName': 'green', 'points': [] } } },
        {'mapShare': 'DustinRomney', 'mapAuth': None, 'mapData': {
            'name' : 'Dustin', 'data':{'color': '#a76114', 'colorName': 'brown', 'points': [] } } },
    ]
    
    
    
        : Arizona 2018 Hunt Party :
        
    hunters = [
     {'mapShare': 'LaurenceWheelock', 'mapAuth': None, 'mapData': {
            'name' : 'Lance', 'data':{'color': '#147516', 'colorName': 'green', 'points': [] } } },
    {'mapShare': 'DustinRomney', 'mapAuth': None, 'mapData': {
            'name' : 'Dustin', 'data':{'color': '#a76114', 'colorName': 'brown', 'points': [] } } },
    ]
    
    results = []
    i = 0
    
    for hunter in hunters:
        if hunter['mapAuth']:
            headers = { 'Authorization': 'Basic {0}'.format(hunter['mapAuth']) }
        else:
            headers = {}

        url = 'https://share.delorme.com/feed/share/{0}?d1={1}T02:00Z'.format(hunter['mapShare'], startDate) 
    
        r = requests.get(url, headers=headers)
        data = xmlparse(r.text, 'lxml')

        try:
            placemarks = data.document.folder.findAll('placemark')
        
            results.append(hunter['mapData'])
            
            for p in placemarks[:-1]:
                results[i]['data']['points'].append([
                    float(p.find(attrs={'name':'Latitude'}).value.text),
                    float(p.find(attrs={'name':'Longitude'}).value.text),
                    p.find(attrs={'name':'Time'}).value.text ])
            
            i += 1 # Success count for debug
        except Exception, err:
            dprint("swordpoint.lib.utils.map_activity [placemarks bs4]", i, err)
            
    return results

def test_map_activity():
    url = 'https://share.delorme.com/feed/share/LaurenceWheelock?d1=2016-09-01T08:00-700'
    r = requests.get(url)
    data = xmlparse(r.text, 'lxml')
    
    placemarks = data.document.folder.findAll('placemark')
    
    results = [ {'name' : 'Lance', 'data':{'color': '#147516', 'colorName': 'green', 'points': [] } } ]
    
    for p in placemarks[:-1]:
        results[0]['data']['points'].append([
            float(p.find(attrs={'name':'Latitude'}).value.text),
            float(p.find(attrs={'name':'Longitude'}).value.text),
            p.find(attrs={'name':'Time'}).value.text ])
    
    return results


    : Icon Activity Functions :

def get_model(icon):
     Return SQLAlchemy object to store in correct table 
    
    try: 
        iconObj = globals()[icon.capitalize()]
    
    except KeyError as err:
        dprint('swordpoint.lib.utils.get_model [iconObj]', icon, err)
        iconObj = None
        
    return iconObj
    
def status(code):
    
    return json.dumps({'status' : code})

def icon_activity():
     Get Icons Stored in DB 
    
    # Runtime imports
    
    icons = {}
    
    for x in dir(models):
        iconObj = globals()[x]
        jsObj = x.lower()

        if type(iconObj) == DeclarativeMeta and x != 'Base':
            
            icons[jsObj] = []
            
            for icon in iconObj.query.all():
                if jsObj == 'glass':
                    icon.icon = 'natural-feature'
                elif jsObj == 'camp':
                    icon.icon = 'campground'
                elif jsObj == 'info':
                    icon.icon = 'square-pin'
                elif jsObj == 'danger':
                    icon.icon = 'map-pin'
                elif jsObj == 'deer':
                    icon.icon = 'crosshairs'
                
                icons[jsObj].append({
                    'label': icon.label, 
                    'desc' : icon.desc, 
                    'lat' : icon.lat, 
                    'lon' : icon.lon, 
                    'icon': icon.icon, 
                    'id' : icon.id,
                    }
                )
    
    return icons

def add_marker(req):
    data = req.json
    dprint(data)
    
    Obj = get_model(data['icon'])
    
    if Obj is None:
        return status('error')
    
    try: 
        new_marker = Obj(label = data['label'], lat=data['lat'], lon=data['lon'], desc=data['desc'])
    
    except AttributeError as err:
        dprint('swordpoint.lib.utils.add_marker [new_marker]', data, err)    
        return status('error')
    
    try:
        db_session.add(new_marker)
        db_session.commit()

    except Exception as err:
        dprint('swordpoint.lib.utils.add_marker [sqlalchemy err]', err)
        return status('error')
    
    return status('ok')

def delete_icon(obj, id):
     Delete Icon from Database 
    
    iconObj = globals()[obj.capitalize()]

    try:
        db_session.delete(iconObj.query.filter(iconObj.id==id).first())
        db_session.commit()
    except Exception as err:
        dprint('swordpoint.lib.utils.delete_icon [sqlalchemy]', obj, id)
    
    return 
'''