#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python migrateAccount.py <portal> <username> <password> <oldOwner> <newOwner>

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

def addUsersToGroups(users, groups, token, portalUrl):
    '''
    REQUIRES ADMIN ACCESS.
    Add users to multiple groups and return a list of the status.
    '''
    # Provide one or more usernames in a list.
    # e.g. ['john_doe', 'jane_doe']
    # Provide one or more group IDs in a list.
    # e.g. ['d93aabd856f8459a8905a5bd434d4d4a',
    #       'f84c841a3dfc4591b1ff83281ea5025f']
    summary = []

    # Assign users to the specified group(s).
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    for group in groups:
        response = urllib.urlopen(portalUrl +
                                  '/sharing/rest/community/groups/' +
                                  group + '/addUsers?',
                                  'users=' + ','.join(users) + "&" +
                                  parameters).read()
        # The response will only report back users that
        # were NOT successfully added.
        summary.append({'id': group, 'results': json.loads(response)})

    return summary

def reassignGroups(newOwner, groups, token, portalUrl):
    '''
    REQUIRES ADMIN ACCESS.
    Changes the owner of a group.
    '''
    # Provide one or more group IDs in a list.
    # e.g. ['d93aabd856f8459a8905a5bd434d4d4a',
    #       'f84c841a3dfc4591b1ff83281ea5025f']
    summary = []

    # Assign users to the specified group(s).
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    for group in groups:
        request = (portalUrl + '/sharing/rest/community/groups/' +
                    group + '/reassign?' + parameters)
        postData = {'targetUsername': newOwner}
        response = urllib.urlopen(request, urllib.urlencode(postData)).read()
        summary.append({'id': group, 'results': json.loads(response)})

    return summary

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
                                         '/sharing/rest/content/items/' +
                                         itemId + '?' + params).read())
    return itemInfo

def getUserInfo(username, token, portalUrl):
    '''Returns information about the specified user.'''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/community/users/' + username +
               '?' + parameters)
    userInfo = json.loads(urllib.urlopen(request).read())
    return userInfo

def updateUserInfo(username, info, token, portalUrl):
    '''Updates a user's info.'''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/community/users/' + username +
               '/update?' + parameters)
    status = json.loads(
        urllib.urlopen(request, urllib.urlencode(info)).read()
    )
    return status

def updateUserRole(username, role, token, portalUrl):
    '''Updates a user's info.'''
    parameters = urllib.urlencode({'token': token,
                                   'f': 'json',
                                   'user': username,
                                   'role': role})
    request = (portalUrl + '/sharing/rest/portals/self/updateUserRole?')
    status = json.loads(
        urllib.urlopen(request, parameters).read()
    )
    return status

def createFolder(username, newFolderName, token, portalUrl):
    '''Creates a new folder in a User's content.'''
    parameters = urllib.urlencode(
        {'token': token,
         'title': newFolderName,
         'f': 'json'}
        )
    request = (portalUrl + '/sharing/rest/content/users/' + username +
               '/createFolder?' + parameters)
    status = json.loads(
        urllib.urlopen(request, parameters).read()
    )
    return status

def migrateAccount(portal, username, password, oldOwner, newOwner, retainExactFolderName=False):
    # Get an admin token.
    token = generateToken(username=username, password=password,
                          portalUrl=portal)

    # Get a list of the oldOwner's folders and any items in root.
    userContent = getUserContent(oldOwner, '/', token, portalUrl=portal)
    newUserContent = getUserContent(newOwner, '/', token, portalUrl=portal)
    
    userInfo = getUserInfo(oldOwner, token, portalUrl=portal)
    newInfo = {'fullName': userInfo['fullName'],
               'description': userInfo['description'],
               'units': userInfo['units']}
    if userInfo.has_key('firstName'):
        newInfo['firstName'] = userInfo['firstName']
    if userInfo.has_key('firstName'):
            newInfo['lastName'] = userInfo['lastName']
    ## Thumbnail migration not working
    #if userInfo.has_key('thumbnail'):
        #newInfo['thumbnail'] =  (portal + '/sharing/rest/community/users/' +
                                 #oldOwner + '/info/' + userInfo['thumbnail'])

    # Check if the user is assigned a custom role.
    if 'roleId' in userInfo.keys():
        newRole = userInfo['roleId']
    else:
        newRole = userInfo['role']

    print 'Updating {}\'s profile'.format(newOwner)
    updateUserInfo(newOwner, newInfo, token, portal)
    print 'Updating {}\'s role'.format(newOwner)
    updateUserRole(newOwner, newRole, token, portal)
    ownedGroups = []
    memberGroups = []
    for group in userInfo['groups']:
        if group['owner'] == oldOwner:
            ownedGroups.append(group['id'])
        else:
            memberGroups.append(group['id'])
    print 'Reassigning ' + str(len(ownedGroups)) + ' groups to ' + newOwner
    reassignGroups(newOwner, ownedGroups, token, portal)
    print 'Adding ' + newOwner + ' to ' + str(len(memberGroups)) + ' groups'
    addUsersToGroups([newOwner], memberGroups, token, portal)

    # *** CAUTION ***
    # The following code will transfer ownership of ALL CONTENT
    # from oldOwner to newOwner.
    # Be sure you are absolutely sure you want to do this before proceeding.
    if not ('items' in userContent or len(userContent['items']) == 0) and (len(userContent['folders']) == 0):
        print oldOwner + ' doesn\'t have any content visible to this account or has no items.'
        print 'Be sure you are signed in as admin.'
    else:
        for item in userContent['items']:
            changeOwnership(item['id'], newOwner, '/', token=token,
                            portalUrl=portal)
        for folder in userContent['folders']:
            if len(folder) == 0:
                continue
            if retainExactFolderName is True:
                if folder['title'] not in [newfolder['title'] for newfolder in newUserContent['folders']]:
                    print "trying to put item into new folder, but no folder exists, creating new folder..."
                    try:
                        createFolder(newOwner, folder['title'], token, portal)
                        print "created folder: " + folder['title']
                    except:
                        print "failed to create folder: " + folder['title']
            folderContent = getUserContent(oldOwner, folder['id'],
                                           token=token, portalUrl=portal)
            for item in folderContent['items']:
                changeOwnership(item['id'], newOwner, folder['title'],
                                token=token, portalUrl=portal)
        print 'Migration completed.'
        print 'All items transferred from {0} to {1}'.format(oldOwner,
                                                             newOwner)

    return 'Migration from {0} to {1} complete.'.format(oldOwner, newOwner)

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('portal',
                        help=('url of the Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('username', help='username')
    parser.add_argument('password', help='password')
    parser.add_argument('oldOwner', help='source account to migrate from')
    parser.add_argument('newOwner', help='destination account to migrate to')
    parser.add_argument('retainExactFolderName', help='True or False. True: exact folder name recreated. \
                                                        False: username_foldername format followed')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal[:-1] if args.portal[-1:] == '/' else args.portal
    username = args.username
    password = args.password
    oldOwner = args.oldOwner
    newOwner = args.newOwner
    retainExactFolderName = args.retainExactFolderName

    migrateAccount(portal, username, password, oldOwner, newOwner, retainExactFolderName)
