#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python migrateRoles.py <portal> -o <portalAdmin> -s <portalPassword>

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

def getPortalInfo(token, portalUrl):
    ''''''
    parameters = urllib.urlencode({'token': token, 'f': 'json'})
    request = (portalUrl + '/sharing/rest/portals/self' + '?' + parameters)
    portalInfo = json.loads(urllib.urlopen(request).read())
    return portalInfo

def getUsers(portalId, token, portalUrl):
    '''Returns a list of all users in the Portal.'''

    # Iterable function to gather all pages of users.
    def __users__(portal, portalId, token, num=100, start=0):
        '''Retrieve a single page of search results.'''
        parameters = urllib.urlencode({'num': num,
                                       'start': start,
                                       'token': token,
                                       'f': 'json'})
        request = (portalUrl + '/sharing/rest/portals/' + portalId +
                   '/users?' + parameters)
        results = json.loads(urllib.urlopen(request).read())
        return results

    allUsers = []
    users = __users__(portalUrl, portalId, token)
    allUsers.extend(users['users'])

    while 'nextStart' in users.iterkeys() and users['nextStart'] != -1:
        users = __users__(portalUrl, portalId, token,
                          start=users['nextStart'])
        allUsers.extend(users['users'])

    return allUsers

def getRoles(token, portalUrl):
    '''Get the custom roles available in the Portal.'''
    ## Currently does not handle for than 100 roles.
    parameters = urllib.urlencode({'token': token,
                                   'f': 'json',
                                   'num': 100})
    request = (portalUrl + '/sharing/rest/portals/self/roles' +
               '?' + parameters)
    roles = json.loads(urllib.urlopen(request).read())
    return roles

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
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal[:-1] if args.portal[-1:] == '/' else args.portal
    username = args.portalAdmin
    password = args.portalPassword

    # Sample usage
    token = generateToken(username=username, password=password,
                          portalUrl=portal)

    # Get the Portal ID.
    portalId = getPortalInfo(token, portal)['id']

    # Get a list of the Portal's roles.
    roles = getRoles(token, portal)

    # Add the built-in roles to the list.
    roles['roles'].extend([{'id': 'account_user',
                            'name': 'User (built-in)'},
                           {'id': 'account_publisher',
                            'name': 'Publisher (built-in)'},
                           {'id': 'account_admin', 'name':
                            'Admin (built-in)'}])

    print 'Available roles'
    for key, role in enumerate(roles['roles']):
        # Add a key to let the user select by number.
        role['key'] = key
        print '{0}. {1}'.format(role['key'], role['name'])
    selection = input('Enter the number of the old role: ')
    oldRole = roles['roles'][selection]

    selection = input('Enter the number of the new role: ')
    newRole = roles['roles'][selection]

    confirm = raw_input('Confirm migration of ' + oldRole['name'] + ' to ' +
                    newRole['name'] + ' (y/n): ')

    if confirm == 'y':
        # Get a list of the Portal's users.
        users = getUsers(portalId, token, portalUrl=portal)

        count = 0
        for user in users:
            if user['role'] == oldRole['id']:
                print 'Migrating ' + user['username']
                updateUserRole(user['username'], newRole['id'], token, portal)
                count += 1

        print 'Migrated {} users from {} to {}.'.format(str(count),
                                                        oldRole['name'],
                                                        newRole['name'])
    elif confirm == 'n':
        print 'Canceling'
        exit()