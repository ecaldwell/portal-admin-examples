#!/usr/bin/env python

# Sample Usage
# python updateItemMetadata.py -u https://www.arcgis.com -o username -s password -i itemId -p 'path/to/metadata.xml'

import argparse
import json
import os
import urllib
import requests
import webbrowser

portal = 'https://www.arcgis.com'
authMethod = 'Built-In' # SAML | Built-In
verify = True # Set to False to ignore certificate validation warnings.
######## Complete for SAML login ############
appId = ''
appSecret = ''
redirectUri = 'urn:ietf:wg:oauth:2.0:oob'
#############################################

def generateToken(username, password, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = {'username': username,
                  'password': password,
                  'client': 'referer',
                  'referer': portalUrl,
                  'expiration': 60, # token life in minutes
                  'f': 'json'}
    url = '{}/sharing/rest/generateToken'.format(portalUrl)
    response = requests.post(url, data=parameters)
    return response.json()

def oAuthAuthorize(clientId, responseType, redirectUri, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({'client_id': clientId,
                                   'response_type': responseType,
                                   'redirect_uri': redirectUri,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/oauth2/authorize?',
                              parameters).read()
    print(response)
    try:
        jsonResponse = json.loads(response)
        if 'access_token' in jsonResponse:
            return jsonResponse['access_token']
        elif 'error' in jsonResponse:
            print(jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print(detail)
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e

def oAuthToken(clientId, clientSecret, redirectUri, grantType, code, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({'client_id': clientId,
                                   'client_secret': clientSecret,
                                   'redirect_uri': redirectUri,
                                   'grant_type': grantType,
                                   'code': code,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/oauth2/token?',
                              parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'access_token' in jsonResponse:
            return jsonResponse['access_token']
        elif 'error' in jsonResponse:
            print jsonResponse['error']['message']
            for detail in jsonResponse['error']['details']:
                print detail
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e
        
def itemDescription(itemId, portalUrl, token):
    '''Retrieves an item's description object.'''
    parameters = {'token': token,
                  'f': 'json'}
    url = '{}/sharing/rest/content/items/{}'.format(portalUrl, itemId)
    response = requests.get(url, params=parameters)
    print(response)
    return response.json()

def updateItemMetadata(username, folder, itemId, file, portalUrl, token):
    '''Uploads an ArcCatalog xml file containing metadata to an item.'''
    parameters = {'token': token,
                  'f': 'json'}
    files = {'metadata': open(file, 'rb')}
    url = '{}/sharing/rest/content/users/{}/{}/items/{}/update'.format(portalUrl, username, folder, itemId)
    response = requests.post(url, data=parameters, files=files, verify=verify)
    return response.json()


# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal',
                        help=('url of the portal (e.g. '
                              'https://webadaptor.domain.com/arcgis)'))
    parser.add_argument('-o', '--username', required=True, help='username')
    parser.add_argument('-s', '--password', required=False, help='password')
    parser.add_argument('-i', '--itemId', help='the item to update')
    parser.add_argument('-p', '--path', help='path to the shapefiles')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    itemId = args.itemId
    path = args.path

    # Authenticate with the portal.
    if authMethod == 'SAML':
        # Use SAML
        parameters = urllib.urlencode({'client_id': appId,
                                       'response_type': 'code',
                                       'redirect_uri': redirectUri})
        authUrl = '{}/sharing/rest/oauth2/authorize?{}'.format(portal, parameters)
        webbrowser.open(authUrl)

        # Get the user's authentication code.
        authCode = raw_input('Enter the code you received: ')

        # Get a token with the authentication code.
        token = oAuthToken(clientId=appId, clientSecret=appSecret, redirectUri=redirectUri, grantType='authorization_code', code=authCode, portalUrl=portal)
    else:
        # Use built-in auth.
        token = generateToken(username, password, portal)['token']

    # Get the item's folder.
    description = itemDescription(itemId=itemId, portalUrl=portal, token=token)

    # Update the item's metadata.
    print('Updating the metadata')
    update = updateItemMetadata(username=username, folder=description['ownerFolder'], itemId=itemId, file=path, portalUrl=portal, token=token)

    print('Finished.')