#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python registerServices.py -u <portal> -o <username> -s <password> -l <REST endpoint>

import urllib
import json
import argparse

def generateToken(username, password, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({
        'username': username,
        'password': password,
        'client': 'referer',
        'referer': portalUrl,
        'expiration': 60,
        'f': 'json'
    })
    response = urllib.urlopen(portalUrl + '/sharing/rest/generateToken?', parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print(jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print(detail)
    except ValueError, e:
        print('An unspecified error occurred.')
        print(e)

def userFolders(portalUrl, username, token):
    '''Return a list of the user's folders.'''
    parameters = {
        'token': token,
        'f': 'json'
    }
    request = portalUrl + '/sharing/rest/content/users/' + username + '/?' + urllib.urlencode(parameters)
    response = urllib.urlopen(request).read()
    return json.loads(response)['folders']

def registerService(username, folder, name, description, serviceUrl, portalUrl, token, thumbnailUrl=''):
    '''Register the service in the user's portal.'''
    parameters = description.copy()
    parameters.update({
        'title': name,
        'type': 'Map Service',
        'url': serviceUrl,
        'overwrite': 'false',
        'thumbnailurl': thumbnailUrl,
        'token' : token,
        'f': 'json'
    })
    parameters_safe = __encode_dict__(parameters)
    request = portalUrl + '/sharing/rest/content/users/' + username + '/' + folder + '/addItem?'
    response = urllib.urlopen(request, urllib.urlencode(parameters_safe)).read()
    return json.loads(response)

def getServices(restUrl):
    '''Return the services and folders at the root of the Services directory.'''
    request = restUrl + '?f=json'
    response = urllib.urlopen(request).read()
    return json.loads(response)

def serviceName(serviceUrl):
    '''Return the service's basic info.'''
    request = serviceUrl + '?f=json'
    response = urllib.urlopen(request).read()
    return json.loads(response)

def serviceInfo(serviceUrl):
    '''Return the description object for the service.'''
    request = serviceUrl + '/info/iteminfo?f=json'
    response = urllib.urlopen(request).read()
    return json.loads(response)

def __encode_dict__(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Encode it in UTF-8.
            v.decode('utf8')
        out_dict[k] = v
    return out_dict

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal', required=True,
                        help=('url of the portal '
                              '(e.g. https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('-o', '--username', required=True, help='username')
    parser.add_argument('-s', '--password', required=True, help='password')
    parser.add_argument('-l', '--rest', required=True,
                        help=('ArcGIS for Server REST endpoint'))
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal[:-1] if args.portal[-1:] == '/' else args.portal
    username = args.username
    password = args.password
    restUrl = args.rest

    # Get a token to use with subsequent requests.
    token = generateToken(username=username, password=password, portalUrl=portal)

    restInfo = getServices(restUrl)
    folders = restInfo['folders']
    services = restInfo['services']

    availableFolders = userFolders(portal, username, token)
    availableFolders.insert(0, {'title': 'Root (Top Level)', 'id': ''})

    print('User folders')
    for key, folder in enumerate(availableFolders):
        # Add a key to let the user select by number.
        folder['key'] = key
        print('{0}. {1}'.format(folder['key'], folder['title']))
    selection = input('Enter the number for the destination folder: ')
    userFolder = availableFolders[selection]['id']

    print('Harvesting services from {}'.format(restUrl))
    for folder in folders:
        folderServices = getServices(restUrl + '/' + folder)['services']
        services.extend(folderServices)

    for service in services:
        serviceUrl = '{}/{}/{}'.format(restUrl, service['name'], service['type'])
        print('Registering {}/{}'.format(service['name'], service['type']))
        description = serviceInfo(serviceUrl)
        name = description['name'] if 'name' in description else service['name']
        thumbnail = '{}/info/thumbnail/{}'.format(serviceUrl, description['thumbnail']) if 'thumbnail' in description else None
        # Convert arrays to comma separated strings for posting.
        for k, v in description.iteritems():
            if isinstance(v, list):
                description[k] = ', '.join([str(x) for x in v])

        result = registerService(username, userFolder, name, description, serviceUrl, portal, token, thumbnail)
        if 'success' in result:
            print('OK')
        elif 'error' in result:
            print('Failed to register {}'.format(name))
