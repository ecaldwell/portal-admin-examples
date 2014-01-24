## Use Cases

#### [addUsersToGroups.py](addUsersToGroups.py)
This example adds members to specific groups within the organization. This is useful if you want new members to immediately have access to the organization's relevant content when they first sign into Portal for ArcGIS.

#### [changeOwnership.py](changeOwnership.py)
This example transfers the ownership of all of the Portal for ArcGIS content owned by a member to another member. You may need to transfer ownership if you are attempting to remove a member (a member cannot be removed if they own content or groups).

#### [copyItem.py](copyItem.py)
This example copies an item from one Portal for ArcGIS (A) into another Portal for ArcGIS (B). The item ownership from Portal for ArcGIS A is transfered to the account specified in Portal for ArcGIS B. This is useful in organizations that have two portals. For example, one for internal and external use or an organization that implements a development and production environment. This script can also be used to move items from Portal for ArcGIS to ArcGIS Online and vice versa.

#### [inviteUsers.py](inviteUsers.py)
This example automatically invites new users and emails them with an activation link. An admin may find this script useful when first setting up a Portal for ArcGIS or for automating the invite of new organization employees on a regular basis. The usernames can be specified to adhere to an organization standard.

#### [updateWebmapServices.py](updateWebmapServices.py)
This example updates the URL of a map service referenced in a web map in Portal for ArcGIS. This is useful if the map service URL has changed and you don't want users to require users to remove and re-add the service to the web map. There are many reasons a service URL may change. For example, the service may have been migrated to a new server, the name of the service was changed, or the service was moved to a different folder on the server.