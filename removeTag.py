#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python removeTag.py <portalUrl> <adminUser> <adminPassword>
#                                 <query> <unwantedTag>
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
            results = __search__(portalUrl=portalUrl, query=query,
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


def removeTag(itemId, unwantedTag, token, portalUrl):
    '''Removes the unwanted tag from an item.'''
    try:
        params = urllib.urlencode({'token' : token,
                                   'f' : 'json'})
        print 'Found item ' + itemId + ' with unwanted tag...'

        # Get the item info
        itemInfo = json.loads(urllib.urlopen(portalUrl + "/sharing/rest/content/items/" + itemId + "?" + params).read())

        # Find items with the unwanted tag and remove it
        if unwantedTag in itemInfo['tags']:
            tags = itemInfo['tags']
            print 'Tags before: ' + ', '.join(tags)
            tags.remove(unwantedTag)
            print 'Tags after: ' + ', '.join(tags)
            strTags = ', '.join(tags)
            ownerFolder = itemInfo['ownerFolder'] if itemInfo['ownerFolder'] else '/'
            modRequest = urllib.urlopen(portalUrl +
                                        '/sharing/content/users/' +
                                        itemInfo['owner'] +
                                        '/' + ownerFolder +
                                        '/items/' + itemId +
                                        '/update?' + params ,
                                        urllib.urlencode(
                                            {'tags' : strTags}
                                        ))

            # Evaluate the results to make sure it happened
            modResponse = json.loads(modRequest.read())
            if modResponse.has_key('error'):
                raise AGOPostError(itemId, modResponse['error']['message'])
            else:
                print 'Successfully removed the unwanted tag from ' + itemInfo['id']

    except ValueError as e:
        print 'Error - no item specified'
    except AGOPostError as e:
        print e.item
        print 'Error updating item ' + e.item + ': ' + e.msg

class AGOPostError(Exception):
    def __init__(self, item, msg):
        print 'ok'
        self.item = item
        self.msg = msg

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('portal',
                        help=('url of the Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('username', help='username')
    parser.add_argument('password', help='password')
    parser.add_argument('query', help='search string to find content')
    parser.add_argument('unwantedTag', help='the tag to remove')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    query = args.query
    unwantedTag = args.unwantedTag

    # Get a token for the source Portal for ArcGIS.
    token = generateToken(username=username, password=password,
                          portalUrl=portal)

    # Get a list of the content matching the query.
    content = searchPortal(portalUrl=portal,
                           query=query,
                           token=token)
    if len(content) == 0:
        print 'No items returned with query \'' + query + '\''
        for item in content:
            removeTag(item['id'], unwantedTag, token=token, portalUrl=portal)

    print 'Update complete.'