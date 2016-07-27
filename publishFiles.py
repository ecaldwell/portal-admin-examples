#!/usr/bin/env python

# Sample Usage
# python publishShapefiles.py -u https://www.arcgis.com -o username -s password -p 'path/to/my/shapefiles'

import argparse
import json
import os
import time
import csv
import urllib
import requests
import webbrowser

portal = 'https://www.arcgis.com'
authMethod = 'Built-In' # SAML | Built-In
verify = True # Set to False to ignore certificate validation warnings.
######## Complete for SAML login ############
appId = ''
appSecret = ''
redirectUri = 'urn:ietf:wg:oauth:2.0:oob'
#############################################

maxJobs = 5 # Set the max number of concurrent jobs allowed.
sleepTime = 60 # Time in seconds to wait between status checks.

def generateToken(username, password, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = {'username': username,
                  'password': password,
                  'client': 'referer',
                  'referer': portalUrl,
                  'expiration': 60, # token life in minutes
                  'f': 'json'}
    url = '{}/sharing/rest/generateToken'.format(portalUrl)
    response = requests.post(url, data=parameters)
    return response.json()

def oAuthAuthorize(clientId, responseType, redirectUri, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({'client_id': clientId,
                                   'response_type': responseType,
                                   'redirect_uri': redirectUri,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/oauth2/authorize?',
                              parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'access_token' in jsonResponse:
            return jsonResponse['access_token']
        elif 'error' in jsonResponse:
            print(jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print(detail)
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e

def oAuthToken(clientId, clientSecret, redirectUri, grantType, code, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({'client_id': clientId,
                                   'client_secret': clientSecret,
                                   'redirect_uri': redirectUri,
                                   'grant_type': grantType,
                                   'code': code,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/oauth2/token?',
                              parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'access_token' in jsonResponse:
            return jsonResponse['access_token']
        elif 'error' in jsonResponse:
            print jsonResponse['error']['message']
            for detail in jsonResponse['error']['details']:
                print detail
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e

def userContent(username, portalUrl, token):
    '''Returns the user's folders and content in the root folder.'''
    parameters = {'token': token,
                  'f': 'json'}
    url = '{}/sharing/rest/content/users/{}'.format(portalUrl, username)
    response = requests.get(url, params=parameters, verify=verify)
    return response.json()

def createFolder(title, username, portalUrl, token):
    '''Creates a new folder in the user's account.'''
    parameters = {'title': title,
                  'token': token,
                  'f': 'json'}
    url = '{}/sharing/rest/content/users/{}/createFolder'.format(portalUrl, username)
    response = requests.post(url, data=parameters, verify=verify)
    return response.json()

def addFileItem(username, folder, file, type, portalUrl, token):
    '''Creates a new item in the user's content.'''
    fileName = os.path.split(file)[-1].split('.')[0]
    # need to break out handlers for files over 10mb
    parameters = {'file': file,
                  'type': type,
                  'title': fileName,
                  # 'multipart': 'true',
                  'token': token,
                  'f': 'json'}
    files = {'file': open(file, 'rb')}
    url = '{}/sharing/rest/content/users/{}/{}/addItem'.format(portalUrl, username, folder)
    response = requests.post(url, data=parameters, files=files, verify=verify)
    return response.json()

def updateItemMetadata(username, folder, itemId, file, portalUrl, token):
    '''Uploads an ArcCatalog xml file containing metadata to an item.'''
    parameters = {'token': token,
                  'f': 'json'}
    files = {'metadata': open(file, 'rb')}
    url = '{}/sharing/rest/content/users/{}/{}/items/{}/update'.format(portalUrl, username, folder, itemId)
    response = requests.post(url, data=parameters, files=files, verify=verify)
    return response.json()

def publishItem(username, itemId, name, fileType, portalUrl, token, hasStaticData='true', maxRecordCount=2000, capabilities='Query', overwrite='false'):
    '''Publishes a hosted service based on an existing source item.'''
    parameters = {'itemId': itemId,
                  'filetype': fileType,
                  'publishParameters': json.dumps({'hasStaticData': hasStaticData,
                                                   'name': name,
                                                   'maxRecordCount': maxRecordCount,
                                                   'layerInfo': {'capabilities': capabilities}}),
                  'overwrite': overwrite,
                  'token': token,
                  'f': 'json'}
    url = '{}/sharing/rest/content/users/{}/publish'.format(portalUrl, username)
    response = requests.post(url, data=parameters, verify=verify)
    return response.json()

def checkStatus(username, folder, serviceItemId, portalUrl, token, jobId=None, jobType=None):
    '''Creates a new item in a user's content.'''
    parameters = {'jobId': jobId,
                  'jobType': jobType,
                  'token': token,
                  'f': 'json'}
    if jobId != None:
        parameters['jobId'] = jobId
    if jobType != None:
        parameters['jobType'] = jobType
    url = '{}/sharing/rest/content/users/{}/{}/items/{}/status'.format(portalUrl, username, folder, serviceItemId)
    response = requests.get(url, params=parameters)
    return response.json()

def getDescription(itemId, portalUrl, token):
    '''Retrieves an item's description object.'''
    parameters = {'token': token,
                  'f': 'json'}
    url = '{}/sharing/rest/content/items/{}'.format(portalUrl, itemId)
    response = requests.get(url, params=parameters)
    return response.json()

def serviceRecordCount(serviceUrl, token):
    '''Retrieves a token to be used with API requests.'''
    parameters = {'where': '1=1',
                  'returnCountOnly': 'true',
                  'token': token,
                  'f': 'json'}
    url = '{}/0/query'.format(serviceUrl)
    response = requests.get(url, params=parameters)
    return response.json()

def updateResult(results, matchK, matchV, k, v, outfile=None):
    '''Update the specified item in the list of results by matching on a provided key.'''
    result = filter(lambda result: result[matchK] == matchV, results)
    result[0][k] = v
    if outfile:
        writeResults(outfile, results)

def writeResults(outfile, results, portalUrl='https://www.arcgis.com'):
    with open(outfile, 'wb') as output:
        dataWriter = csv.writer(
            output,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL
        )
        # Write header row.
        dataWriter.writerow(
            ['Dataset', 'Size', 'Folder', 'Item Id', 'Item URL', 'Service Id', 'Service URL', 'Status', 'Service Record Count']
        )
        for result in results:
            dataWriter.writerow(
                [result['shortname'],
                 result['size'],
                 result['foldername'],
                 result['itemId'],
                 '{}/home/item.html?id={}'.format(portalUrl, result['itemId']) if result['itemId'] else '',
                 result['serviceItemId'],
                 '{}/home/item.html?id={}'.format(portalUrl, result['serviceItemId']) if result['serviceItemId'] else '',
                 result['status'] if result['status'] else '',
                 result['count'] if result['count'] else '']
            )

def currentJobs():
    return len(jobs)


# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal',
                        help=('url of the portal (e.g. '
                              'https://webadaptor.domain.com/arcgis)'))
    parser.add_argument('-o', '--username', required=True, help='username')
    parser.add_argument('-s', '--password', required=False, help='password')
    parser.add_argument('-p', '--path', help='path to the shapefiles')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal
    username = args.username
    password = args.password
    path = args.path

    # Authenticate with the portal.
    if authMethod == 'SAML':
        # Use SAML
        parameters = urllib.urlencode({'client_id': appId,
                                       'response_type': 'code',
                                       'redirect_uri': redirectUri})
        authUrl = '{}/sharing/rest/oauth2/authorize?{}'.format(portal, parameters)
        webbrowser.open(authUrl)

        # Get the user's authentication code.
        authCode = raw_input('Enter the code you received: ')

        # Get a token with the authentication code.
        token = oAuthToken(clientId=appId, clientSecret=appSecret, redirectUri=redirectUri, grantType='authorization_code', code=authCode, portalUrl=portal)
    else:
        # Use built-in auth.
        token = generateToken(username, password, portal)['token']

    # Gather up the shapefiles in the directory (and subdirectories).
    shapefiles = [] # keep track of all the shapefiles to upload.
    jobs = [] # keep track of active publishing jobs.

    for root, dirs, files in os.walk(path):
        for f in files:
            if f[-4:] == '.zip':
                description = {'shortname': f[:-4].replace(' ', '_'),
                               'filename': f,
                               'foldername': os.path.split(os.path.dirname(os.path.join(root, f)))[1],
                               'path': os.path.join(root, f),
                               'size': round(float(os.path.getsize(os.path.join(root, f))) / 1048576, 3), # bytes to megabytes
                               'metadata': os.path.join(root, '{}.xml'.format(f[:-4])),
                               'itemId': None,
                               'itemUrl': None,
                               'serviceItemId': None,
                               'serviceItemUrl': None,
                               'status': None,
                               'count': None}
                shapefiles.append(description)

    results = list(shapefiles) # Copy the list of shapefiles to track progress.
    resultsFile = '{}/results.csv'.format(path)

    # Check if the destination folders exist in the user's account.
    content = userContent(username, portal, token)
    folders = content['folders']

    while len(shapefiles) > 0 or len(jobs) > 0:
        if len(shapefiles) > 0 and len(jobs) < maxJobs:
            # Continue pushing new jobs.
            shapefile = shapefiles.pop(0)

            # Get the destination folder id and create it if it doesn't exist.
            folder = filter(lambda folder: folder['title'] == shapefile['foldername'], folders)
            if not folder:
                print('Creating folder {}'.format(shapefile['foldername']))
                newFolder = createFolder(shapefile['foldername'], username, portal, token)
                folder = {'title': newFolder['folder']['title'],
                          'id': newFolder['folder']['id']}
                folders.append(folder)
            else:
                folder = folder[0]

            # Create the item in ArcGIS Online.
            print('')
            print('Uploading {} {} mb'.format(shapefile['filename'], shapefile['size']))
            try:
                newItem = addFileItem(username=username, folder=folder['id'], file=shapefile['path'], type='Shapefile', portalUrl=portal, token=token)
                if 'success' in newItem:
                    itemId = newItem['id']
                    print('    created item {}'.format(itemId))
                    updateResult(results, 'shortname', shapefile['shortname'], 'itemId', itemId, outfile=resultsFile)

                     # Update the item's metadata.
                    print('    updating the metadata')
                    update = updateItemMetadata(username=username, folder=folder['id'], itemId=itemId, file=shapefile['metadata'], portalUrl=portal, token=token)
                else:
                    print('    error - {}'.format(newItem['error']['message']))
                    updateResult(results, 'shortname', shapefile['shortname'], 'status', newItem['error']['message'], outfile=resultsFile)
            except:
                print('    error adding {}'.format(shapefile['filename']))
                updateResult(results, 'shortname', shapefile['shortname'], 'status', 'unhandled item upload error', outfile=resultsFile)
                continue

            # Publish it.
            print('    publishing {}'.format(shapefile['shortname']))
            try:
                publishing = publishItem(username, newItem['id'], shapefile['shortname'], 'Shapefile', portal, token, overwrite='false')
                job = publishing['services'][0]
                if 'jobId' in job:
                    job['folderId'] = folder['id']
                    job['shortname'] = shapefile['shortname']
                    jobs.append(job)
                    updateResult(results, 'shortname', job['shortname'], 'serviceItemId', job['serviceItemId'])
                    updateResult(results, 'shortname', job['shortname'], 'status', 'publishing started', outfile=resultsFile)
                else:
                    print('    error - {}'.format(job['error']['message']))
                    updateResult(results, 'shortname', shapefile['shortname'], 'status', job['error']['message'], outfile=resultsFile)
            except:
                print('    error publishing {}'.format(shapefile['shortname']))
                updateResult(results, 'shortname', shapefile['shortname'], 'status', 'unhandled publishing error', outfile=resultsFile)
                continue
        else:
            # Check the status of existing jobs.
            currentJobs = len(jobs)
            while len(jobs) > 0:
                i = -1
                print('')
                print('Checking the status of {} publishing job(s)'.format(currentJobs))
                for job in jobs:
                    i += 1
                    status = checkStatus(username, job['folderId'], job['serviceItemId'], portal, token, jobId=job['jobId'])
                    job['status'] = status['status']
                    if job['status'] in ['completed', 'failed']:
                        description = getDescription(job['serviceItemId'], portal, token)
                        serviceUrl = description['url']
                        count = serviceRecordCount(serviceUrl, token)['count']
                        updateResult(results, 'shortname', job['shortname'], 'count', count)
                        updateResult(results, 'shortname', job['shortname'], 'status', 'publishing {}'.format(job['status']), outfile=resultsFile)
                        jobs.pop(i)
                    else:
                        updateResult(results, 'shortname', job['shortname'], 'status', 'publishing {}'.format(job['status']))
                        continue
                if len(jobs) != 0:
                    print('{} of {} service(s) still publishing'.format(len(jobs), currentJobs))
                    print('Next check in {} seconds'.format(sleepTime))
                    time.sleep(sleepTime)
                    break

    print('')
    print('All services finished publishing')
    print('Check {} for full details on each item.'.format(resultsFile))