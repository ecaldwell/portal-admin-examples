#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python backupContent.py -u <portal> -o <admin> -s <password> -q <query> -f <folder>

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

def searchPortal(portal, query=None, totalResults=None, sortField='numviews',
                 sortOrder='desc', token=None):
    '''
    Search the portal using the specified query and search parameters.
    Optionally provide a token to return results visible to that user.
    '''
    # Default results are returned by highest
    # number of views in descending order.
    allResults = []
    if not totalResults or totalResults > 100:
        numResults = 100
    else:
        numResults = totalResults
    results = __search__(portal, query, numResults, sortField, sortOrder, 0,
                         token)

    if not 'error' in results.keys():
        if not totalResults:
            totalResults = results['total'] # Return all of the results.
        allResults.extend(results['results'])
        while (results['nextStart'] > 0 and
               results['nextStart'] < totalResults):
            # Do some math to ensure it only
            # returns the total results requested.
            numResults = min(totalResults - results['nextStart'] + 1, 100)
            results = __search__(portal=portal, query=query,
                                 numResults=numResults, sortField=sortField,
                                 sortOrder=sortOrder, token=token,
                                 start=results['nextStart'])
            allResults.extend(results['results'])
        return allResults
    else:
        print results['error']['message']
        return results

def __search__(portal, query=None, numResults=100, sortField='numviews',
               sortOrder='desc', start=0, token=None):
    '''Retrieve a single page of search results.'''
    params = {
        'q': query,
        'num': numResults,
        'sortField': sortField,
        'sortOrder': sortOrder,
        'f': 'json',
        'start': start
    }
    if token:
        # Adding a token provides an authenticated search.
        params['token'] = token
    request = portal + '/sharing/rest/search?' + urllib.urlencode(params)
    results = json.loads(urllib.urlopen(request).read())
    return results

def getUserContent(username, portalUrl, token):
    ''''''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/content/users/' + username +
               '?' + parameters)
    content = json.loads(urllib.urlopen(request).read())
    return content

def getItemDescription(itemId, portalUrl, token):
    '''Returns the description for a Portal for ArcGIS item.'''
    parameters = urllib.urlencode({'token' : token,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + "/sharing/rest/content/items/" +
                              itemId + "?" + parameters).read()
    return response

def getItemData(itemId, portalUrl, token):
    '''Returns the description for a Portal for ArcGIS item.'''
    parameters = urllib.urlencode({'token' : token,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + "/sharing/rest/content/items/" +
                              itemId + "/data?" + parameters).read()
    return response

def backupItem(itemId, portalUrl, token, folder):
    description = getItemDescription(itemId, portal, token)
    data = getItemData(itemId, portal, token)
    filePath = '{}/{}'.format(folder, itemId)
    try:
        with open('{}_desc'.format(filePath), 'w') as backupDesc:
            backupDesc.write(description)
        with open('{}_data'.format(filePath), 'w') as backupData:
            backupData.write(data)
        return({'success': itemId})
    except:
        return({'error': itemId})

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal',
                        help=('url of the portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('-o', '--admin', help='admin username')
    parser.add_argument('-s', '--password', help='admin password')
    parser.add_argument('-q', '--query', help='search string to find content')
    parser.add_argument('-f', '--folder', help='local folder to backup to')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    admin = args.admin
    password = args.password
    query = args.query
    folder = args.folder

    # Get a token for the source Portal for ArcGIS.
    token = generateToken(username=admin, password=password, portalUrl=portal)

    # Get a list of the content matching the query.
    content = searchPortal(portal=portal, query=query, token=token)

    # Backup the content to a local folder.
    for item in content:
        try:
            result = backupItem(item['id'], portal, token, folder)
            if 'success' in result:
                print('backed up {}: {}'.format(item['type'], item['title']))
            elif 'error' in result:
                print('couldn\'t backup {}: {}'.format(item['type'], item['title']))
            else:
                print('error backing up {}: {}'.format(item['type'], item['title']))
        except:
            print('error backing up {}: {}'.format(item['type'], item['title']))

    print('Backup complete.')