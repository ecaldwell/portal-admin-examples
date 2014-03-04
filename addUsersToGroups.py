#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python addUsersToGroups.py <portal> <username> <password>
#                            <groupSearchString> <users>
# <users> should be entered as a comma separated string

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

def groupSearch(query, token, portalUrl):
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
        toolSummary.append({'id': group,
                            'results': json.loads(response)})

    return toolSummary

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('portal',
                        help=('url of the Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('username', help='username')
    parser.add_argument('password', help='password')
    parser.add_argument("query", help="group search string")
    parser.add_argument("users", help="a comma-separated string of users")
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    query = args.query
    users = (args.users).split(',') # Create a list from the input users.

    token = generateToken(username=username, password=password,
                          portalUrl=portal)

    # Get a list of the groups matching the query.
    groupIDs = []
    groups = groupSearch(query, token, portal)
    for group in groups:
        groupIDs.append(group['id'])

    results = addUsersToGroups(users=users, groups=groupIDs, token=token,
                           portalUrl=portal)

    for group in results:
        if len(group['results']['notAdded']) > 0:
            # Get the group name.
            groupName = groupSearch('id:' + group['id'], token,
                                    portal)[0]['title']
            print 'The following users were not added to ' + groupName
            for user in group['results']['notAdded']:
                print '    ' + user

    print 'Process complete.'