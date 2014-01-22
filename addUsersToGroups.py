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

    toolSummary = []

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
        toolSummary.append({group: json.loads(response)})

    return toolSummary


# Sample usage
portal = 'https://webadaptor.domain.com/arcgis'
users = ['john_doe', 'jane_doe']
groups = ['d93aabd856f8459a8455a5bd434d4d4a',
          'f84c841a3dfc4341b1ff83281ea5025f']

token = generateToken(username='<username>', password='<password>',
                      portalUrl=portal)

results = addUsersToGroups(users=users, groups=groups, token=token,
                           portalUrl=portal)

print results