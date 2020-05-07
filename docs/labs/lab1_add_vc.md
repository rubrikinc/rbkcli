# Add vCenter Server

1. Add vCenter server:
	
	```
	$ rbkcli vmware vcenter -m post -p hostname=vcsa.xavier.local,username=administrator@vsphere.local,password=Rubrik123\!\!
	{
	  "id": "LITE_REFRESH_METADATA_72ef7f2b-9149-4259-898b-e7edcccd0442_8dc30a06-46bb-4009-af4e-1faa2b3bb5c5:::0",
	  "status": "QUEUED",
	  "progress": 0.0,
	  "startTime": "2020-04-29T11:09:05.843Z",
	  "links": [
		{
		  "href": "https://192.168.1.220/api/v1/vmware/vcenter/request/LITE_REFRESH_METADATA_72ef7f2b-9149-4259-898b-e7edcccd0442_8dc30a06-46bb-4009-af4e-1faa2b3bb5c5:::0",
		  "rel": "self"
		}
	  ]
	}
	```
	
2. Verify if vcenter was added:	
	- Verify status of vCenter task using the output of previous command:
        ```
        $ rbkcli vmware vcenter request LITE_REFRESH_METADATA_72ef7f2b-9149-4259-898b-e7edcccd0442_8dc30a06-46bb-4009-af4e-1faa2b3bb5c5:::0
        {
          "id": "LITE_REFRESH_METADATA_72ef7f2b-9149-4259-898b-e7edcccd0442_8dc30a06-46bb-4009-af4e-1faa2b3bb5c5:::0",
          "status": "SUCCEEDED",
          "startTime": "2020-04-29T11:09:05.843Z",
          "endTime": "2020-04-29T11:09:14.739Z",
          "nodeId": "cluster:::VRVW420847VMW",
          "links": [
            {
              "href": "https://192.168.1.220/api/v1/vmware/vcenter/request/LITE_REFRESH_METADATA_72ef7f2b-9149-4259-898b-e7edcccd0442_8dc30a06-46bb-4009-af4e-1faa2b3bb5c5:::0",
              "rel": "self"
            }
          ]
        }
        ```
    - Verify status of vCenter task using events: 
        ```
        $ rbkcli event -q object_type=Vcenter,object_name=vcsa.xavier.local
        {
          "hasMore": false,
          "data": [
            {
              "id": "2020-04-29:11:0:::1588158554753-53077115-40cb-4a4d-9c4b-5bccf8c5f528",
              "objectId": "vCenter:::72ef7f2b-9149-4259-898b-e7edcccd0442",
              "objectType": "Vcenter",
              "objectName": "vcsa.xavier.local",
              "eventInfo": "{\"message\":\"Finished refreshing vCenter 'vcsa.xavier.local'. Automatically linked '0' Virtual Machines.\",\"id\":\"Vmware.VcenterRefreshSucceeded\",\"params\":{\"${vcenterAddress}\":\"vcsa.xavier.local\",\"${autoResolvedVmCount}\":\"0\"}}",
              "time": "Wed Apr 29 11:09:14 UTC 2020",
              "eventType": "Configuration",
              "eventStatus": "Success",
              "eventSeriesId": "4bfdb53d-eb37-49e4-99e1-0bcdf7252ed7",
              "relatedIds": [
                "vCenter:::72ef7f2b-9149-4259-898b-e7edcccd0442"
              ],
              "jobInstanceId": "LITE_REFRESH_METADATA_72ef7f2b-9149-4259-898b-e7edcccd0442_8dc30a06-46bb-4009-af4e-1faa2b3bb5c5:::0",
              "hasException": false
            }
          ]
        }
        ```

	- List vCenter servers:
        ```
        $ rbkcli vmware vcenter -s id,hostname,username,connectionStatus,version
        [
          {
            "id": "vCenter:::72ef7f2b-9149-4259-898b-e7edcccd0442",
            "hostname": "vcsa.xavier.local",
            "username": "administrator@vsphere.local",
            "connectionStatus": {
              "status": "Connected"
            },
            "version": "6.7.3"
          }
        ]
        ```

3. Verify if VMs were added:
	
	```
	$ rbkcli vmware vm -s id,name,[agentStatus][agentStatus],guestOsName -T
	 id                                                           | name        | agentStatus_agentStatus | guestOsName
	========================================================================================================================================================
	 VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-149 | windows2016 | Unregistered            | Microsoft Windows Server 2016 or later (64-bit)
	 VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-148 | ubuntu1404  | Unregistered            | Ubuntu Linux (64-bit)
	 VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-147 | ubuntu-lamp | Unregistered            | Ubuntu Linux (64-bit)

	**Total amount of objects [3]

	```
 
 
<-- Back to [Useful learning workflows](labs/labs.md)