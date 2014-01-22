#!/usr/bin/env python
import urllib
import json

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
    token = json.loads(response)['token']
    return token

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
    print 'Transfering ownership of item: ' + itemId
    reqUrl = (portalUrl + '/sharing/rest/content/users/' +
              itemInfo['owner'] + '/' + itemInfo['ownerFolder'] +
              '/items/' + itemId + '/reassign?')
    response = json.loads(urllib.urlopen(reqUrl, params).read())
    return response

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


# Sample usage
portal = 'https://webadaptor.domain.com/arcgis'
itemId = 'abcfc80258744e1a82a697dba53e0215'
oldOwner = 'user1'
newOwner = 'user2'
token = generateToken(username='myUsername', password='myPassword',
                      portalUrl=portal)

# Get a list of the oldOwner's folders and any items in root.
userContent = getUserContent(oldOwner, '/', token,
                             portalUrl=portal)

# Change ownership of a single item.
# The item will be placed in the root folder of the new owner.
changeOwnership(itemId, newOwner, '/', token=token, portalUrl=portal)

## *** CAUTION ***
## The following code will transfer ownership of ALL CONTENT
## from oldOwner to newOwner.
## Be sure you are absolutely sure you want to do this before proceeding.
#for item in userContent['items']:
    #changeOwnership(item['id'], newOwner, '/', token=token,
                    #portalUrl=portal)
#for folder in userContent['folders']:
    #folderContent = getUserContent(oldOwner, folder['id'], token=token,
                                   #portalUrl=portal)
    #for item in folderContent['items']:
        #changeOwnership(item['id'], newOwner, folder['title'], token=token,
                        #portalUrl=portal)