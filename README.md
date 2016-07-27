## Use Cases

#### [addOfflineBasemaps.py](addOfflineBasemaps.py)
This example registers all of the new offline-ready basemaps [from this public group in ArcGIS Online](http://www.arcgis.com/home/group.html?owner=esri&title=Tiled%20Basemaps) and burns in the Portal admin's user credentials so that Portal users may use these maps without needing to authenticate in ArcGIS Online. These maps are required for disconnected editing support in Collector for ArcGIS.
###### Sample Usage
Add all offline-ready basemaps to the folder "Offline Basemaps" in the Portal admin's account and burn in the ArcGIS Online credentials.

`python addOfflineBasemaps.py addOfflineBasemaps.py -a ago_admin -p pass.word -u https://webadaptor.domain.com/arcgis -o admin -s pass.word -f 'Offline Basemaps'`

#### [addUsersToGroups.py](addUsersToGroups.py)
This example adds members to specific groups within the organization. This is useful if you want new members to immediately have access to the organization's relevant content when they first sign into Portal for ArcGIS.
###### Sample Usage
Add `user1`, `user2`, and `user3` to all groups with the keyword "Operations"

`python addUsersToGroups.py https://portal.domain.com:7443/arcgis admin password Operations user1,user2,user3`

#### [batchMigrateAccounts.py](addUsersToGroups.py)
This script automates the usage of [migrateAccount.py](migrateAccount.py) by reading the old account and new account names from a spreadsheet (see [UserListExample.csv](UserListExample.csv) for an example spreadsheet layout).

###### Sample Usage
Migrate all content and group memberships and ownerships for the users in `UserList.csv`.

`python batchMigrateAccounts.py -u https://www.arcgis.com -o admin -s adminPassword -c UserList.csv True`

#### [changeOwnership.py](changeOwnership.py)
This example transfers the ownership of all of the Portal for ArcGIS content owned by a member to another member. You may need to transfer ownership if you are attempting to remove a member (a member cannot be removed if they own content or groups).
###### Sample Usage
Transfer ownership of all content from user `johndoe` to user `janedoe`

`python changeOwnership.py https://portal.domain.com:7443/arcgis admin password johndoe janedoe`

#### [copyContent.py](copyContent.py)
This example copies an item from one Portal for ArcGIS (A) into another Portal for ArcGIS (B). The item ownership from Portal for ArcGIS A is transfered to the account specified in Portal for ArcGIS B. This is useful in organizations that have two portals. For example, one for internal and external use or an organization that implements a development and production environment. This script can also be used to move items from Portal for ArcGIS to ArcGIS Online and vice versa.
###### Sample Usage
Copy all content owned by `johndoe` in Portal A to new user `janedoe` in Portal B

`python copyContent.py https://portalA.domain.com:7443/arcgis admin password owner:johndoe https://portalB.domain.com:7443/arcgis admin password janedoe /`

#### [createCsvOfGroupUsers.py](createCsvOfGroupUsers.py)
This example creates a spreadsheet listing the groups and members that match the supplied group search string. The default filename is `group_details.csv` and will be created in the script directory. Optionally specify a filepath with the `-f` argument.
###### Sample Usage
Create a CSV of all `public` groups with the keyword `fire`.

`python createCsvOfGroupUsers.py -u https://portalA.domain.com:7443/arcgis -o admin -s password -q 'fire access:public'`

#### [createCsvOfUsers.py](createCsvOfUsers.py)
This example creates a spreadsheet of all the users in a portal including their full name, username, email, and role. The default filename is `portal_users.csv` and will be created in the script directory. Optionally specify a filepath with the `-f` argument.
###### Sample Usage
Create a CSV of my portal's users.

`python createCsvOfUsers.py -u https://portalA.domain.com:7443/arcgis -o admin -s password`

#### [migrateAccount.py](migrateAccount.py)
This example migrates an entire account from one user to another including their content, group memberships, and group ownerships. This may be useful if you are migrating users to enterprise logins and wish to transfer their existing account to their new enterprise account username.
###### Sample Usage
Migrate all content, group memberships, and group ownerships from account `john` to account `john_enterprise`, retaining exact folder names in the new account.

`python migrateAccount.py https://portal.domain.com:7443/arcgis admin password john john_enterprise True`

#### [migrateRoles.py](migrateRoles.py)
This example changes the role of all users with Role A to Role B. This may be useful if you are setting up custom roles and wish to transfer all  users with the built-in Publisher role to the new custom role.
###### Sample Usage
Migrate all users in the Portal with Role A to Role B.

`python migrateRoles.py -u https://portal.domain.com:7443/arcgis -o admin -s password`

#### [registerServices.py](registerServices.py)
This script registers all of the services from an ArcGIS for Server REST endpoint in the user's portal.
###### Sample Usage
Register the services at https://server.domain.com/arcgis/rest/services.

`python registerServices.py -u https://portal.domain.com:7443/arcgis -o admin -s password -l https://server.domain.com/arcgis/rest/services`

#### [updateItemMetadata.py](updateItemMetadata.py)
This example updates an item's description page using an xml file with the ArcGIS metadata format. These files can be generated in ArcGIS Desktop using the [Export Metadata tool](http://desktop.arcgis.com/en/arcmap/latest/tools/conversion-toolbox/export-metadata.htm) with the `FGDC2ESRI_ISO.xml` translator. This is useful when you have detailed metadata associated with a dataset that you would like carried over when you publish it to your portal.
###### Sample Usage
Update the item details for portal item `abc123` using the metadata in `new_metadata.xml`.

`python updateItemMetadata.py -u https://www.arcgis.com -u admin -s password -i abc123 -p new_metadata.xml`

#### [updateWebmapServices.py](updateWebmapServices.py)
This example updates the URL of a map service referenced in a web map in Portal for ArcGIS. This is useful if the map service URL has changed and you don't want users to require users to remove and re-add the service to the web map. There are many reasons a service URL may change. For example, the service may have been migrated to a new server, the name of the service was changed, or the service was moved to a different folder on the server.
###### Sample Usage
Replace the domain prefix `http://server.domainA.com` with `http://server.domainB.com` for all web maps in the Portal

`python updateWebmapServices.py https://portal.domain.com:7443/arcgis admin password "type: Web Map" http://server.domainA.com http://server.domainB.com`
