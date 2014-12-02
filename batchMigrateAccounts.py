#!/usr/bin/env python
# Requires Python 2.7+

# Sample Usage:
# python batchMigrateAccounts.py -u https://www.arcgis.com -o adminUsername
#                                -s adminPassword -c UserList.csv

import argparse
import csv
import migrateAccount

# Run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--portal',
                        help=('url of the Portal (e.g. '
                              'https://portal.domain.com:7443/arcgis)'))
    parser.add_argument('-o', '--username', help='admin username')
    parser.add_argument('-s', '--password', help='admin password')
    parser.add_argument('-c', '--csv', help='path to the csv')
    # Read the command line arguments.
    args = parser.parse_args()
    portal = args.portal[:-1] if args.portal[-1:] == '/' else args.portal
    username = args.username
    password = args.password
    csvPath = args.csv

with open(csvPath, 'rU') as usersCsv:
    users = csv.reader(usersCsv, delimiter=',')
    next(users) # Skip the header row.
    for user in users:
        print 'Migrating {} to {}.'.format(user[0], user[1])
        migrateAccount.migrateAccount(portal, username, password,
                                      user[0], user[1])
