#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python copyContent.py <sourcePortal> <sourceAdmin> <sourcePassword>
#                       <query> <destinationPortal> <destAdmin>
#                       <destPassword> <destOwner> <destFolder>

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

def addItem(username, folder, description, data, portalUrl, token,
                thumbnailUrl=''):
    '''Creates a new item in a user's content.'''
    parameters = urllib.urlencode({'item': json.loads(description)['title'],
                                   'text': data,
                                   'overwrite': 'false',
                                   'thumbnailurl': thumbnailUrl,
                                   'token' : token,
                                   'f' : 'json'})
    postParameters = (urllib.urlencode(json.loads(description))
                      .replace('None', '') + '&' + parameters)
    response = urllib.urlopen(portalUrl + '/sharing/rest/content/users/' +
                              username + '/' + folder + '/addItem?',
                              postParameters).read()
    return response

def copyItem(itemId, destinationOwner, destinationFolder, sourcePortal,
             sourceToken, destinationPortal=None, destinationToken=None):
    '''
    Copies an item into a user's account in the specified folder.
    Use '/' as the destination folder when moving content into root.
    '''
    # This function defaults to copying into the same Portal
    # and with the same token permissions as the source account.
    # If the destination is a different Portal then specify that Portal url
    # and include a token with permissions on that instance.
    if not destinationPortal:
        destinationPortal = sourcePortal
    if not destinationToken:
        destinationToken = sourceToken
    description = getItemDescription(itemId, sourcePortal, sourceToken)
    data = getItemData(itemId, sourcePortal, sourceToken)
    thumbnail = json.loads(description)['thumbnail']
    if thumbnail:
        thumbnailUrl = (sourcePortal + '/sharing/rest/content/items/' +
                        itemId + '/info/' + thumbnail +
                        '?token=' + sourceToken)
    else:
        thumbnailUrl = ''
    status = addItem(destinationOwner, destinationFolder, description,
                         data, destinationPortal, destinationToken,
                         thumbnailUrl)
    return json.loads(status)

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcePortal',
                        help=('url of the source Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('sourceAdmin', help='source admin username')
    parser.add_argument('sourcePassword', help='source admin password')
    parser.add_argument("query", help='search string to find content')
    parser.add_argument('destPortal',
                        help=('url of the destination Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('destAdmin', help='destination admin username')
    parser.add_argument('destPassword', help='destination admin password')
    parser.add_argument('owner', help='destination account to copy to')
    parser.add_argument('folder', help='destination folder to copy to')
    # Read the command line arguments.
    args = parser.parse_args()
    sourcePortal = args.sourcePortal
    sourceAdmin = args.sourceAdmin
    sourcePassword = args.sourcePassword
    query = args.query
    destPortal = args.destPortal
    destAdmin = args.destAdmin
    destPassword = args.destPassword
    owner = args.owner
    folder = args.folder

    # Get a token for the source Portal for ArcGIS.
    sourceToken = generateToken(username=sourceAdmin, password=sourcePassword,
                          portalUrl=sourcePortal)

    # Get a token for the destination Portal for ArcGIS.
    destToken = generateToken(username=destAdmin, password=destPassword,
                              portalUrl=destPortal)

    # Get the destination folder ID.
    folderId = ''
    destUser = getUserContent(owner, destPortal, destToken)
    for folder in destUser['folders']:
        if folder['title'] == folder:
            folderId = folder['id']

    # Get a list of the content matching the query.
    content = searchPortal(portal=sourcePortal,
                           query=query,
                           token=sourceToken)

    # Copy the content into the destination user's account.
    for item in content:
        try:
            result = copyItem(item['id'], owner, folderId, sourcePortal,
                              sourceToken, destPortal, destToken)
            if 'success' in result:
                print 'successfully copied ' + item['type'] + ': ' + item['title']
            elif 'error' in result:
                print 'error copying ' + item['type'] + ': ' + item['title']
                print result['error']['message']
                for detail in result['error']['details']:
                    print detail
            else:
                print 'error copying ' + item['type'] + ': ' + item['title']
        except:
            'error copying ' + item['type'] + ': ' + item['title']

    print 'Copying complete.'