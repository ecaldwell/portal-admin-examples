#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python updateWebmapServices.py <sourcePortal> <sourceAdmin> <sourcePassword>
#                                <query> <oldUrl> <newUrl>

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

def searchPortal(portalUrl, query=None, totalResults=None, sortField='numviews',
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
    results = __search__(portalUrl, query, numResults, sortField, sortOrder, 0,
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

def __search__(portalUrl, query=None, numResults=100, sortField='numviews',
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

def updateWebmapService(webmapId, oldUrl, newUrl, token, portalUrl):
    '''Replaces the URL for a specified map service in a web map.'''
    try:
        params = urllib.urlencode({'token' : token,
                                   'f' : 'json'})
        print 'Getting Info for: ' + webmapId
        # Get the item data.
        reqUrl = (portalUrl + '/sharing/content/items/' + webmapId +
                  '/data?' + params)
        itemDataReq = urllib.urlopen(reqUrl).read()
        itemString = str(itemDataReq)

        # Find the service URL to be replaced.
        if itemString.find(oldUrl) > -1:
            newString = itemString.replace(oldUrl, newUrl)
            # Get the item's info for the addItem parameters
            itemInfoReq = urllib.urlopen(portalUrl +
                                         '/sharing/content/items/' +
                                         webmapId + '?' + params)
            itemInfo = json.loads(itemInfoReq.read(),
                                  object_hook=__decodeDict__)
            print 'Updating ' + itemInfo['title']

            # Post back the changes overwriting the old map
            modRequest = urllib.urlopen(portalUrl +
                                        '/sharing/content/users/' +
                                        itemInfo['owner'] +
                                        '/' + itemInfo['ownerFolder'] +
                                        '/items/' + webmapId +
                                        '/update?' + params ,
                                        urllib.urlencode(
                                            {'text' : newString}
                                        ))

            # Evaluate the results to make sure it happened
            modResponse = json.loads(modRequest.read())
            if modResponse.has_key('error'):
                raise AGOPostError(webmapId, modResponse['error']['message'])
            else:
                print 'Successfully updated the urls'
        else:
            print 'Didn\'t find any services with ' + oldUrl
    except ValueError as e:
        print 'Error - no web map specified'
    except AGOPostError as e:
        print e.webmap
        print 'Error updating web map ' + e.webmap + ': ' + e.msg

# Helper functions for decoding the unicode values in the webmap json.
def __decodeDict__(dct):
    newdict = {}
    for k, v in dct.iteritems():
        k = __safeValue__(k)
        v = __safeValue__(v)
        newdict[k] = v
    return newdict

def __safeValue__(inVal):
    outVal = inVal
    if isinstance(inVal, unicode):
        outVal = inVal.encode('utf-8')
    elif isinstance(inVal, list):
        outVal = __decode_list__(inVal)
    return outVal

def __decode_list__(lst):
    newList = []
    for i in lst:
        i = __safeValue__(i)
        newList.append(i)
    return newList

class AGOPostError(Exception):
    def __init__(self, webmap, msg):
        print 'ok'
        self.webmap = webmap
        self.msg = msg

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('portal', help='url of the portal')
    parser.add_argument('username', help='username')
    parser.add_argument('password', help='password')
    parser.add_argument('query', help='search string to find content')
    parser.add_argument('oldUrl', help='the URL to replace')
    parser.add_argument('newUrl', help='the new URL')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    query = args.query
    oldUrl = args.oldUrl
    newUrl = args.newUrl

    # Get a token for the source Portal for ArcGIS.
    token = generateToken(username=username, password=password,
                          portalUrl=portal)

    # Get a list of the content matching the query.
    content = searchPortal(portalUrl=portal,
                           query=query,
                           token=token)

    for item in content:
        if item['type'] == 'Web Map':
            updateWebmapService(item['id'], oldUrl, newUrl, token=token,
                                portalUrl=portal)

    print 'Update complete.'