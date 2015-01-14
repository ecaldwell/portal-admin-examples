#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python createCsvOfUsers.py -u <portal> -o <username> -s <password>
#                            -f <filename>

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

def getUsers(token, portalUrl):
    '''
    Returns a list of all users in the organization (requires admin access).
    '''
    def __portalId__(token, portalUrl):
        '''
        Return the id of the portal. If null, then this is the
        default portal for anonymous and non-organizational users.
        '''
        parameters = urllib.urlencode(
            {'token': token, 'f': 'json'}
        )
        request = '{}/sharing/rest/portals/self?{}'.format(
            portalUrl, parameters
        )
        response = json.loads(urllib.urlopen(request).read())
        return response['id']

    def __users__(portalId, start=0):
        '''Retrieve a single page of users.'''
        parameters = urllib.urlencode(
            {'token': token, 'f': 'json', 'start': start, 'num': 100}
        )
        request = '{}/sharing/rest/portals/{}/users?{}'.format(
            portalUrl, portalId, parameters
        )
        users = json.loads(urllib.urlopen(request).read())
        return users

    portalId = __portalId__(token, portalUrl)
    allUsers = []
    users = __users__(portalId)
    for user in users['users']:
        allUsers.append(user)
    while users['nextStart'] > 0:
        users = __users__(portalId, users['nextStart'])
        for user in users['users']:
            allUsers.append(user)
    return allUsers

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
    parser.add_argument('-f', '--filename', required=False,
                        default='portal_users.csv',
                        help=('the path to the file to create '
                              '(default: portal_users.csv'))
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal[:-1] if args.portal[-1:] == '/' else args.portal
    username = args.username
    password = args.password
    filename = args.filename

    token = generateToken(username, password, portal)
    # Create a dictionary of the portal's roles.
    customRoles = getRoles(token, portal)
    roles = {}
    for role in customRoles['roles']:
        roles[role['id']] = role['name']
    # Add the built-in roles to the list.

    roles.update({
        'account_user': 'User (built-in)',
        'account_publisher': 'Publisher (built-in)',
        'account_admin': 'Admin (built-in)',
        'org_user': 'User (built-in)',
        'org_publisher': 'Publisher (built-in)',
        'org_admin': 'Admin (built-in)'
    })

    users = getUsers(token, portal)

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
            ['Full Name', 'Username', 'Email', 'Role']
        )

        print('Found {} users.'.format(len(users)))

        for user in users:
            userData = {}
            for attr in ['fullName', 'username', 'email', 'role']:
                try:
                    userData[attr] = user[attr].encode('utf-8')
                except:
                    pass
            userData['role'] = roles[user['role']]
            dataWriter.writerow([
                userData['fullName'],
                userData['username'],
                userData['email'],
                userData['role']
            ])

    print('\nFinished creating {}'.format(filename))