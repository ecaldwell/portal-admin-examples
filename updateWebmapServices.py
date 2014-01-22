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


# Sample usage
portal = 'https://webadaptor.domain.com/arcgis'
webmapId = 'e90cf123c1ee472495a4178f4b74ac1d'
oldUrl = 'http://oldServer.com/serviceName/MapServer'
newUrl = 'http://newServer.com/serviceName/MapServer'

token = generateToken(username='<username>', password='<password>',
                      portalUrl=portal)
updateWebmapService(webmapId, oldUrl, newUrl, token=token,
                    portalUrl=portal)
