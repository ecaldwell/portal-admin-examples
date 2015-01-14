#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python createCsvOfGroupUsers.py -o <portal> -u <username> -s <password>
#                                 -q <group search string> -f <filename>

import urllib
import json
import argparse
import csv

def generateToken(username, password, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode(
        {'username' : username, 'password' : password, 'client' : 'referer',
         'referer': portalUrl, 'expiration': 60, 'f' : 'json'}
    )
    response = urllib.urlopen(portalUrl + '/sharing/rest/generateToken?',
                              parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print(jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print(detail)
    except ValueError, e:
        print('An unspecified error occurred.')
        print(e)

def searchGroups(query, token, portalUrl):
    '''Returns a list of all folders for the specified user.'''
    ## Currently does more than 100 groups.
    parameters = urllib.urlencode(
        {'q': query, 'num': 100, 'token': token, 'f': 'json'})
    request = '{}/sharing/rest/community/groups?{}'.format(
        portalUrl, parameters
    )
    groups = json.loads(urllib.urlopen(request).read())
    return groups

def getGroupUsers(groupId, token, portalUrl):
    '''Lists the users, owner, and administrators of a given group.'''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = '{}/sharing/rest/community/groups/{}/users?{}'.format(
        portalUrl, groupId, parameters
    )
    users = json.loads(urllib.urlopen(request).read())
    return users

def getRoles(token, portalUrl):
    '''Get the custom roles available in the portal.'''
    ## Does not handle more than 100 roles.
    parameters = urllib.urlencode({
        'token': token, 'f': 'json', 'num': 100
    })
    request = '{}/sharing/rest/portals/self/roles?{}'.format(
        portalUrl, parameters
    )
    roles = json.loads(urllib.urlopen(request).read())
    return roles

def getUser(username, token, portalUrl):
    '''A user resource representing a registered user of the portal.'''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = '{}/sharing/rest/community/users/{}?{}'.format(
        portalUrl, username, parameters
    )
    user = json.loads(urllib.urlopen(request).read())
    return user

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal', required=True,
                        help=('url of the portal '
                              '(e.g. https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('-o', '--username', required=True, help='username')
    parser.add_argument('-s', '--password', required=True, help='password')
    parser.add_argument('-q', '--query', required=True,
                        help='group query to search')
    parser.add_argument('-f', '--filename', required=False,
                        default='group_details.csv',
                        help=('the path to the file to create '
                              '(default: group_details.csv'))
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal[:-1] if args.portal[-1:] == '/' else args.portal
    username = args.username
    password = args.password
    query = args.query
    filename = args.filename

    token = generateToken(username, password, portal)

    groups = searchGroups(query, token, portal)

    print('Found {} group(s) with search "{}"'.format(groups['total'], query))

    customRoles = getRoles(token, portal)
    roles = {}
    for role in customRoles['roles']:
        roles[role['id']] = role['name']

    outputFile = filename
    with open(outputFile, 'wb') as output:
        dataWriter = csv.writer(
            output,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL
        )
        # Write header row.
        dataWriter.writerow(
            ['Group Name', 'Full Name', 'Email', 'Username', 'Role']
        )

        for group in groups['results']:
            users = getGroupUsers(group['id'], token, portal)
            print('Processing {}'.format(group['title']))
            groupMembers = []
            for user in users['users']:
                groupMembers.append(user)
            for admin in users['admins']:
                groupMembers.append(admin)
            for member in groupMembers:
                userInfo = getUser(member, token, portal)
                userData = {
                    'fullName': '',
                    'username': '',
                    'email': '',
                    'role': ''
                }
                for attr in ['fullName', 'username', 'email', 'role']:
                    try:
                        userData[attr] = userInfo[attr].encode('utf-8')
                    except:
                        pass
                    if 'roleId' in userInfo:
                        userData['role'] = roles[userInfo['roleId']]
                dataWriter.writerow([
                    group['title'],
                    userData['fullName'],
                    userData['email'],
                    userData['username'],
                    userData['role']
                ])

    print('\nFinished creating {}'.format(filename))