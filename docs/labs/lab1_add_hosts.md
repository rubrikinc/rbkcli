# ADD AND PROTECT HOSTS

1. Try and run the command that adds a host to the CDM:
    ```
    rksupport@nested-rbkcli:~$ rbkcli host -m post -p hostname="nested-windows.xavier.local"
    {
      "message": "Timed out while getting certificate at nested-windows.xavier.local:12801"
    }
    ```
    - You might receive a message similar to this, which means you need to troubleshoot connectivity.
    - From the CDM you are trying to add the host to, open the SSH CLI and test connection with:
    
        ```
        VRVW420847VMW >> network netcat -vnz 192.168.1.8 12800-12801
        netcat: connect to 192.168.1.8 12800 port [tcp]: Connection timed out
        netcat: connect to 192.168.1.8 12801 port [tcp]: Connection timed out
        ```
    - Fix whatever issues might be happening on the network and try again (in my case just needed to add a rule on Windows Firewall):
        ```
        VRVW420847VMW >> network netcat -vnz 192.168.1.8 12800-12801
        Connection to 192.168.1.8 12800 port [tcp/*] succeeded!
        Connection to 192.168.1.8 12801 port [tcp/*] succeeded!
        ```
    - Try adding the host now:
        ``` 
        rksupport@nested-rbkcli:~$ rbkcli host -m post -p hostname="nested-windows.xavier.local"
        {
          "agentId": "{56ae4023-9c53-4aef-a4e5-7bfb572daa90}",
          "operatingSystemType": "Windows",
          "mssqlCbtEffectiveStatus": "OffDefault",
          "compressionEnabled": false,
          "primaryClusterId": "616fdf1b-68ea-4ec0-84a1-8bea2b9c51fb",
          "mssqlCbtDriverInstalled": false,
          "operatingSystem": "Windows Server 2016 Standard 64-bit",
          "hostVfdEnabled": "Enabled",
          "hostname": "nested-windows.xavier.local",
          "hostVfdDriverState": "NotInstalled",
          "isRelic": false,
          "name": "nested-windows.xavier.local",
          "id": "Host:::8c1b3273-68f6-4308-b750-75896da100d9",
          "mssqlCbtEnabled": "Default",
          "status": "Connected"
        }
        ```


2. Protect a host:

1. Find the command to protect a host:
    - Filter all commands for an endpoint that contains sla_domain and method is post:
        ```
        $ rbkcli commands -f endpoint~sla_domain,method=post -T
         version  | endpoint                | method | summary
        =======================================================================================================
         internal | sla_domain {id} assign  | post   | Assign managed entities to an SLA Domain synchronously.
         v1       | mssql sla_domain assign | post   | Assign SLA properties to SQL Server objects
         v1       | sla_domain              | post   | Create SLA Domain
         v2       | sla_domain {id} pause   | post   | Pause an SLA Domain
         v2       | sla_domain              | post   | Create SLA Domain
        
        **Total amount of objects [5]
        
        ```
2. Use the found command to protect the host:
    ```
    $ rbkcli sla_domain e83e69f0-646f-4a7d-b1be-ef03af8068c3 assign -p '{"managedIds": ["Host:::e0ea6920-0495-473a-92d5-e68c8db4b965"]}' -m post
    {
      "errorType": "user_error",
      "message": "SlaHolder with managed id Host:::e0ea6920-0495-473a-92d5-e68c8db4b965 not found",
      "cause": null
    }

    ```
    - CDM cannot protect a host by itself, we need to define which part of the Host we want to protect: Fileset, Volumes, MSSQL?
    - We will go wit Fileset for this example.

3. Create Host Fileset:
    - Run the command to create the host fileset:
        ```
        $ rbkcli fileset -m post -p hostId=Host:::e0ea6920-0495-473a-92d5-e68c8db4b965
        The request content was malformed:
        org.json4s.package$MappingException: No usable value for templateId
        Did not find value which can be converted into java.lang.String
        ```
    - The error message returned by the server, mentions `No usable value for templateId`, let's find out a command with the word template on it and related to filesets.
        ```
        $ rbkcli commands -f endpoint~fileset,summary~template -T
         version  | endpoint              | method | summary
        ===============================================================================================
         internal | fileset_template bulk | delete | Delete fileset templates.
         internal | fileset_template bulk | patch  | Modify fileset templates.
         internal | fileset_template bulk | post   | Create fileset templates.
         v1       | fileset_template {id} | delete | Delete a fileset template
         v1       | fileset_template {id} | get    | Get information for a fileset template
         v1       | fileset_template {id} | patch  | Modify a fileset template
         v1       | fileset_template      | get    | Get summary information for all fileset templates
         v1       | fileset_template      | post   | Create a fileset template
        
        **Total amount of objects [8]
        ```
    - A fileset_template is needed in order to create a host fileset, so let's create that first:
        ```
        rksupport@nested-rbkcli:~$ rbkcli fileset_template -m post -p '{"name": "WindowsFileset","includes": ["C:\\**"],"operatingSystemType":"Windows"}'
        {
          "excludes": [],
          "operatingSystemType": "Windows",
          "primaryClusterId": "616fdf1b-68ea-4ec0-84a1-8bea2b9c51fb",
          "isArchived": false,
          "includes": [
            "C:\\**"
          ],
          "isArrayEnabled": false,
          "allowBackupNetworkMounts": true,
          "exceptions": [],
          "shareCount": 0,
          "allowBackupHiddenFoldersInNetworkMounts": true,
          "hostCount": 0,
          "useWindowsVss": true,
          "name": "WindowsFileset",
          "id": "FilesetTemplate:::70045ff5-d409-4120-b7ed-aff12665734a"
        }

        ```
    - Lets list the fileset_template's that exist in the cluster, with the name we've given:
        ```
        rksupport@nested-rbkcli:~$ rbkcli fileset_template -f name=WindowsFileset -s id,name
        [
          {
            "id": "FilesetTemplate:::70045ff5-d409-4120-b7ed-aff12665734a",
            "name": "WindowsFileset"
          }
        ]
        ```
    
    - Let's list the host we want to protect, also filtering the name:
        ```
        rksupport@nested-rbkcli:~$ rbkcli host -s id,name=nested-windows.xavier.local
        [
          {
            "id": "Host:::8c1b3273-68f6-4308-b750-75896da100d9",
            "name": "nested-windows.xavier.local"
          }
        ]
        ```
    - Let's get both IDs from previous command and create a host fileset:
        ```
        rksupport@nested-rbkcli:~$ rbkcli fileset -m post -p templateId=FilesetTemplate:::70045ff5-d409-4120-b7ed-aff12665734a,hostId=Host:::8c1b3273-68f6-4308-b750-75896da100d9
        {
          "hostName": "nested-windows.xavier.local",
          "excludes": [],
          "effectiveSlaDomainId": "UNPROTECTED",
          "primaryClusterId": "616fdf1b-68ea-4ec0-84a1-8bea2b9c51fb",
          "configuredSlaDomainId": "UNPROTECTED",
          "isPassthrough": false,
          "templateId": "FilesetTemplate:::70045ff5-d409-4120-b7ed-aff12665734a",
          "allowBackupNetworkMounts": true,
          "isConfiguredSlaDomainRetentionLocked": false,
          "allowBackupHiddenFoldersInNetworkMounts": true,
          "id": "Fileset:::03ce1fb5-3380-49c9-9a99-cbb5a520c823",
          "operatingSystemType": "Windows",
          "isEffectiveSlaDomainRetentionLocked": false,
          "configuredSlaDomainName": "Unprotected",
          "hostId": "Host:::8c1b3273-68f6-4308-b750-75896da100d9",
          "includes": [
            "C:\\**"
          ],
          "archivedSnapshotCount": 0,
          "exceptions": [],
          "enableHardlinkSupport": false,
          "snapshots": [],
          "templateName": "WindowsFileset",
          "enableSymlinkResolution": false,
          "useWindowsVss": true,
          "isRelic": false,
          "snapshotCount": 0,
          "name": "WindowsFileset"
        }
        ```
4. Protect the Host Fileset:
    - With the ID of the Fileset created let's assign it to an SLA:
        ```
        $ rbkcli sla_domain 4c399fc1-f7f0-48f0-8eda-bbf1c8640582 assign -m post -p '{"managedIds": ["Fileset:::03ce1fb5-3380-49c9-9a99-cbb5a520c823"]}'
        Response code: 204
        Response text:
        ```
    - Let's find a backup event related to this protection to confirm it is working:
        ```
        rksupport@nested-rbkcli:~$ rbkcli event -q event_type=Backup,object_ids=Fileset:::03ce1fb5-3380-49c9-9a99-cbb5a520c823
        {
          "hasMore": false,
          "data": [
            {
              "id": "2020-04-30:14:4:::1588257797960-e8fda0ca-b156-4ea0-914b-8b1c73a3384a",
              "objectId": "Fileset:::03ce1fb5-3380-49c9-9a99-cbb5a520c823",
              "objectType": "WindowsFileset",
              "objectName": "WindowsFileset",
              "eventInfo": "{\"message\":\"Retrieving data for fileset 'WindowsFileset' from 'nested-windows.xavier.local' using node VRVW420847VMW.\",\"id\":\"Fileset.FilesetDataFetchStarted\",\"params\":{\"${filesetName}\":\"WindowsFileset\",\"${source}\":\"nested-windows.xavier.local\",\"${nodeId}\":\"VRVW420847VMW\"}}",
              "time": "Thu Apr 30 14:43:17 UTC 2020",
              "eventType": "Backup",
              "eventStatus": "Running",
              "eventSeriesId": "405ac517-a6a6-4945-af2e-714954d829c0",
              "eventProgress": "31.25",
              "isCancelable": true,
              "isCancelRequested": false,
              "relatedIds": [
                "Fileset:::03ce1fb5-3380-49c9-9a99-cbb5a520c823"
              ],
              "jobInstanceId": "CREATE_FILESET_SNAPSHOT_03ce1fb5-3380-49c9-9a99-cbb5a520c823:::0",
              "hasException": false
            }
          ]
        }
        ```


<-- Back to [Useful learning workflows](labs/labs.md)