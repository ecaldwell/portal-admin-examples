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

def copyItem(itemId, destinationOwner, sourcePortal, sourceToken,
             destinationFolder='/', destinationPortal=None,
             destinationToken=None):
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


# Sample usage.
portalA = 'https://webadaptor.domainA.com/arcgis'
portalB = 'https://webadaptor.domainB.com/arcgis'
itemId = '16318e12374a4090aebb9b93564d88cd'

# Get a token for the source Portal for ArcGIS.
tokenA = generateToken(username='<source_username>', password='<password>',
                      portalUrl=portalA)

# Get a token for the destination Portal for ArcGIS.
tokenB = generateToken(username='<dest_username>', password='<password>',
                      portalUrl=portalB)

# Copy the item into the destination user's root folder.
print copyItem(itemId, '<destination_username>', portalA, tokenA,
               '/', portalB, tokenB)