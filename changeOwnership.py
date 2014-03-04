#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python changeOwnership.py <portal> <username> <password>
#                           <oldOwner> <newOwner>

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

def changeOwnership(itemId, newOwner, newFolder, token, portalUrl):
    '''
    REQUIRES ADMIN ACCESS.
    Transfers ownership of all content from one user to another.
    Use '/' as the destination folder when moving content into root.
    '''
    itemInfo = getItemInfo(itemId, token, portalUrl)
    params = urllib.urlencode({'targetUsername': newOwner,
                               'targetFoldername': newFolder,
                               'token' : token,
                               'f' : 'json'})
    if not itemInfo['ownerFolder']:
        itemInfo['ownerFolder'] = '/'
    reqUrl = (portalUrl + '/sharing/rest/content/users/' +
              itemInfo['owner'] + '/' + itemInfo['ownerFolder'] +
              '/items/' + itemId + '/reassign?')
    response = urllib.urlopen(reqUrl, params).read()
    try:
        jsonResponse = json.loads(response)
        if 'success' in jsonResponse:
            print 'Item ' + itemId + ' has been transferred.'
        elif 'error' in jsonResponse:
            print 'Error transferring item ' + itemId + '.'
            for detail in jsonResponse['error']['details']:
                print detail
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e

def getUserContent(username, folder, token, portalUrl):
    '''Returns a list of all folders for the specified user.'''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/content/users/' + username +
               '/' + folder + '?' + parameters)
    userContent = json.loads(urllib.urlopen(request).read())
    return userContent

def getItemInfo(itemId, token, portalUrl):
    '''Returns general information about the item.'''
    params = urllib.urlencode({'token' : token,
                               'f' : 'json'})
    itemInfo = json.loads(urllib.urlopen(portalUrl +
                                         '/sharing/content/items/' +
                                         itemId + '?' + params).read())
    return itemInfo

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('portal',
                        help='https://portal.domain.com:7443/arcgis')
    parser.add_argument('username', help='username')
    parser.add_argument('password', help='password')
    parser.add_argument("oldOwner", help="source account to migrate from")
    parser.add_argument("newOwner", help="destination account to migrate to")
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    oldOwner = args.oldOwner
    newOwner = args.newOwner

    # Sample usage
    token = generateToken(username=username, password=password,
                          portalUrl=portal)

    # Get a list of the oldOwner's folders and any items in root.
    userContent = getUserContent(oldOwner, '/', token,
                                 portalUrl=portal)

    # *** CAUTION ***
    # The following code will transfer ownership of ALL CONTENT
    # from oldOwner to newOwner.
    # Be sure you are absolutely sure you want to do this before proceeding.
    if not 'items' in userContent:
        print oldOwner + ' doesn\'t have any content visible to this account.'
        print 'Be sure you are signed in as admin.'
    else:
        for item in userContent['items']:
            changeOwnership(item['id'], newOwner, '/', token=token,
                            portalUrl=portal)
        for folder in userContent['folders']:
            folderContent = getUserContent(oldOwner, folder['id'],
                                           token=token, portalUrl=portal)
            for item in folderContent['items']:
                changeOwnership(item['id'], newOwner, folder['title'],
                                token=token, portalUrl=portal)
        print 'Migration completed.'
        print 'All items transferred from {0} to {1}'.format(oldOwner,
                                                             newOwner)

