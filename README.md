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

#### [updateWebmapServices.py](updateWebmapServices.py)
This example updates the URL of a map service referenced in a web map in Portal for ArcGIS. This is useful if the map service URL has changed and you don't want users to require users to remove and re-add the service to the web map. There are many reasons a service URL may change. For example, the service may have been migrated to a new server, the name of the service was changed, or the service was moved to a different folder on the server.
###### Sample Usage
Replace the domain prefix `http://server.domainA.com` with `http://server.domainB.com` for all web maps in the Portal

`python updateWebmapServices.py https://portal.domain.com:7443/arcgis admin password "type: Web Map" http://server.domainA.com http://server.domainB.com`