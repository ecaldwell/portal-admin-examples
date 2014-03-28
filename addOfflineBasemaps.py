#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python addOfflineBasemaps.py -u <destinationPortal> -o <portalAdmin>
#                              -s <portalPassword> -f <destFolder>
#                              -a <agoUsername> -p <agoPassword>

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
                 sortOrder='desc', token=''):
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

def groupSearch(query, portalUrl, token=''):
    '''Search for groups matching the specified query.'''
    # Example 1: query all groups owned by a user.
    # 'owner:johndoe'
    # Example 2: query groups with Operations in the name.
    # 'Operations'
    # Example 3: query all groups with public access.
    # 'access:public'
    parameters = urllib.urlencode({'q': query, 'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/community/groups?' + parameters)
    groups = json.loads(urllib.urlopen(request).read())
    return groups['results']

def getUserContent(username, portalUrl, token):
    ''''''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/content/users/' + username +
               '?' + parameters)
    content = urllib.urlopen(request).read()
    return json.loads(content)

def getItemDescription(itemId, portalUrl, token=''):
    '''Returns the description for a Portal for ArcGIS item.'''
    parameters = urllib.urlencode({'token' : token,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + "/sharing/rest/content/items/" +
                              itemId + "?" + parameters).read()
    return json.loads(unicode(response, 'utf-8'))

def createFolder(username, title, portalUrl, token):
    '''Creates a new folder in a user's content.'''
    parameters = urllib.urlencode({'title': title,
                                   'token' : token,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/content/users/' +
                              username + '/createFolder?', parameters).read()
    return json.loads(response)

def addServiceItem(username, folder, description, serviceUrl, portalUrl,
                   token, thumbnailUrl='', serviceUsername=None,
                   servicePassword=None):
    '''Creates a new item in a user's content.'''
    # Update the description with unicode safe values.
    descriptionJSON = __decodeDict__(json.loads(description))
    parameters = {'item': descriptionJSON['title'],
                  'url': serviceUrl,
                  'thumbnailurl': thumbnailUrl,
                  'overwrite': 'false',
                  'token' : token,
                  'f' : 'json'}

    if serviceUsername and servicePassword:
        # Store the credentials with the service.
        parameters.update({'serviceUsername': serviceUsername,
                           'servicePassword': servicePassword})

    # Add the item's description (with safe values for unicode).
    parameters.update(descriptionJSON)

    # Encode and post the item.
    postParameters = urllib.urlencode(parameters)
    response = urllib.urlopen(portalUrl + '/sharing/rest/content/users/' +
                              username + '/' + folder + '/addItem?',
                              postParameters).read()
    return json.loads(response)

# Helper functions for decoding the unicode values in the response json.
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

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal', required=True,
                        help=('url of the Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('-o', '--portalAdmin', required=True,
                        help='Portal admin username')
    parser.add_argument('-s', '--portalPassword', required=True,
                        help='Portal admin password')
    parser.add_argument('-f', '--folder', required=False,
                        help='Optional destination folder')
    parser.add_argument('-a', '--agoAdmin', required=False,
                        help='ArcGIS Online admin username')
    parser.add_argument('-p', '--agoPassword', required=False,
                        help='ArcGIS Online admin password')
    # Read the command line arguments.
    args = parser.parse_args()
    agoAdmin = args.agoAdmin
    agoPassword = args.agoPassword
    portal = args.portal
    portalAdmin = args.portalAdmin
    portalPassword = args.portalPassword
    folderTitle = args.folder

    # Get a token for the Portal for ArcGIS.
    print 'Getting token for ' + portal
    token = generateToken(username=portalAdmin, password=portalPassword,
                          portalUrl=portal)

    # Get the destination folder ID.
    folderId = ''
    if folderTitle == None:
        # No folder specified. Folder is root.
        print 'Using the root folder...'
        folderId = '/'
    else:
        # Check if the folder already exists.
        userContent = getUserContent(portalAdmin, portal, token)
        for folder in userContent['folders']:
            if folder['title'] == folderTitle:
                folderId = folder['id']
        # Create the folder if it was not found.
        if folderId == '':
            print 'Creating folder ' + args.folder + '...'
            newFolder = createFolder(portalAdmin, folderTitle, portal, token)
            folderId = newFolder['folder']['id']
        print 'Using folder ' + folderTitle + ' (id:' + folderId + ')'

    # Get the ArcGIS Online group ID.
    query = 'owner:esri title:Tiled Basemaps'
     # Search for the public ArcGIS Online group (no token needed).
    sourceGroup = groupSearch(query, 'https://www.arcgis.com')[0]['id']

    # Get the items in the ArcGIS Online group specified above.
    basemaps = searchPortal('https://www.arcgis.com', 'group:' + sourceGroup)

    # Add the basemaps as new items in the Portal.
    for basemap in basemaps:
        # Get the item description.
        description = getItemDescription(basemap['id'],
                                         'https://www.arcgis.com')
        serviceUrl = description['url']
        thumbUrl = ('https://www.arcgis.com' +
                    '/sharing/rest/content/items/' + description['id'] +
                    '/info/' + description['thumbnail'])

        newDescription = json.dumps(
            {'title': description['title'],
             'type': description['type'],
             'snippet': description['snippet'],
             'description': description['description'],
             'licenseInfo': description['licenseInfo'],
             'tags': ','.join(description['tags']),
             'typeKeywords': ','.join(description['typeKeywords']),
             'accessInformation': description['accessInformation']}
        )

        try:
            result = addServiceItem(portalAdmin, folderId, newDescription,
                                    serviceUrl, portal, token, thumbUrl,
                                    agoAdmin, agoPassword)
            if 'success' in result:
                print 'Successfully added ' + basemap['title']
            elif 'error' in result:
                print 'Error copying ' + basemap['title']
                print result['error']['message']
                for detail in result['error']['details']:
                    print detail
            else:
                print 'Error copying ' + basemap['title']
                print 'An unhandled error occurred.'
        except:
            print 'Error copying ' + basemap['title']
            print 'An unhandled exception occurred.'

    print 'Copying complete.'