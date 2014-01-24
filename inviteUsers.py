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

def checkUsernames(usernames, portalUrl, token):
    '''
    Accepts a string of usernames and returns suggestions.
    If the username is available, the suggestion is the same.
    If the username is unavailable, an alternate suggestion is provided.
    '''
    params = urllib.urlencode({'usernames' : usernames,
                               'token' : token,
                               'f': 'json'})
    response = urllib.urlopen(portalUrl +
                              '/sharing/rest/community/checkUsernames?' +
                              params).read()
    return json.loads(response)

def inviteUsers(users, token, portalUrl):
    '''
    REQUIRES ADMIN ACCESS.
    Sends an email with an activation link to a list of users.
    '''
    # users is a list of dictionaries structured as:
    # {'username' : 'janedoe',
    #  'fullname' : 'Jane Doe',
    #  'email' : 'janedoe@xyz.com',
    #  'role' : 'account_user'}

    subject = 'An invitation to join XYZ\'s Portal for ArcGIS. \
    DO NOT REPLY'

    body = '<html><body>\
<p>Organization XYZ Administrator has invited you to join your \
organization\'s Portal for ArcGIS.</p><p>Please click this link to finish \
setting up your account and establish your password: \
<a href="{portalUrl}/home/newuser.html?invitation=@@invitation.id@@">\
{portalUrl}/home/newuser.html?invitation=@@invitation.id@@</a></p>\
<p>Note that your account has already been created for you with the \
username, <strong>@@touser.username@@</strong> and that usernames are case \
sensitive.  </p><p>If you have difficulty signing in, please email us at \
admin@xyz.com. Be sure to include a description of the problem, the error \
message, and a screenshot.</p><p>For your reference, you can access the \
home page of the organization here: <br>{portalUrl}</p><p>This link will \
expire in two weeks.</p><p style="color:gray;">This is an automated email, \
please do not reply.</p></body></html>'.format(portalUrl=portalUrl)

    params = urllib.urlencode({'invitationList' : {'invitations' : users},
                               'subject' : subject,
                               'html' : body,
                               'token' : token,
                               'f' : 'json'})

    # POST the invite list.
    response = urllib.urlopen(portalUrl +
                              '/sharing/rest/portals/self/invite?',
                              params).read()

    return json.loads(response)


# Sample usage
portal = 'https://webadaptor.domain.com/arcgis'
users = [{'username' : 'jane_doe',
          'fullname' : 'Jane Doe',
          'email' : 'janedoe@xyz.com',
          'role' : 'account_user'},
         {'username' : 'john_doe',
          'fullname' : 'John Doe',
          'email' : 'johndoe@xyz.com',
          'role' : 'account_user'}]

token = generateToken(username='<username>', password='<password>',
                      portalUrl=portal)

# Check if the desired usernames are available.
changes = []
for user in users:
    status = checkUsernames(user['username'], portal, token)['usernames'][0]
    if not status['suggested']==user['username']:
        changes.append('Changed {0} to {1}'.format(user['username'],
                                                   status['suggested']))
        # Change the desired username to the suggestion.
        user['username'] = status['suggested']

# Display any usernames that were changed.
if changes:
    for change in changes:
        print change

# Send the invites.
inviteStatus = inviteUsers(users, token, portal)
print inviteStatus