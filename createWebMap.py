#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python createWebMap.py -p <portalUrl> -u <username> -s <password> -a <comma separated string of services>

import urllib
import json
import argparse

def generateToken(username, password, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({'username' : username,
                                   'password' : password,
                                   'client' : 'referer',
                                   'referer': portalUrl,
                                   'expiration': 60,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/generateToken?',
                              parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print jsonResponse['error']['message']
            for detail in jsonResponse['error']['details']:
                print detail
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e

def addItem(username, folder, description, data, portalUrl, token,
                thumbnailUrl=''):
    '''Creates a new item in a user's content.'''
    parameters = urllib.urlencode({'item': description['title'],
                                   'text': data,
                                   'overwrite': 'false',
                                   'thumbnailurl': thumbnailUrl,
                                   'token' : token,
                                   'f' : 'json'})
    postParameters = (urllib.urlencode(description)
                      .replace('None', '') + '&' + parameters)
    response = urllib.urlopen(portalUrl + '/sharing/rest/content/users/' +
                              username + '/' + folder + '/addItem?',
                              postParameters).read()
    return response

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--portal', required=True, help=('url of the Portal'))
    parser.add_argument('-u', '--username', required=True, help='username')
    parser.add_argument('-s', '--password', required=True, help='password')
    parser.add_argument('-a', '--services', required=True, help='array of services')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    services = args.services

    webmapDescription = {
        "title": "test",
        "type": "Web Map",
        "tags": ["test"]
    }

    webmapJson = """{
        "operationalLayers": [],
        "baseMap": {
            "baseMapLayers": [
                {
                    "id": "defaultBasemap",
                    "layerType": "ArcGISTiledMapServiceLayer",
                    "url": "http://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
                    "visibility": "true",
                    "opacity": 1,
                    "title": "Topographic"
                }
            ],
            "title": "Topographic"
        },
        "spatialReference": {
            "wkid": 102100,
            "latestWkid": 3857
        },
        "version": "2.4"
    }"""

    webmap = json.loads(webmapJson)
    token = token = generateToken(username, password, portal)

    serviceList = services.split(',')
    for service in serviceList:
        layer = json.loads('{}')
        layer['url'] = service
        layer['title'] = "service 1"
        layer['opacity'] = 1

        webmap['operationalLayers'].append(layer)

    webmapJson = json.dumps(webmap)

    print(addItem(username, '/', webmapDescription, webmapJson, portal, token))
