# Get archived snapshots details from all filesets

This is a demonstration of a **Complex command**, for such, the scope of the commands were chosen randomly. The concepts demonstrated could be reused in any command.

### Scenario
For this scenario let's imagine that:
- Your Rubrik CDM version is 5.0.0-p2-1122.
- Your company will no longer use an archive location and you are not sure how many filesets have archived snapshots.
- As your company only backs up filesets, you need to get a list of the filesets snapshots that are archived, so you know which ones to expire or reconfigure.

### What can I do?
1.  As an user, I want to filter commands available and to do that I need to know available filters, so I will run the following:
    ```
    $ rbkcli commands -f ?
    [endpoint]
    [method]
    [summary]
    [version]
    ```
	
2. My only requirement is that the command to be related to filesets or snapshots, therefore I will create a filter for the respective field: endpoint.
    ```
    $ rbkcli commands -f endpoint~fileset -T
     version  | endpoint                     | method | summary
    ======================================================================================================
     internal | host_fileset share {id}      | get    | Get detailed information for a network share.
     internal | host_fileset share           | get    | Get summary information for network shares.
     internal | host_fileset {id}            | get    | Get detail information for a host.
     internal | host_fileset                 | get    | Get summary information for hosts.
     v1       | fileset request {id}         | get    | Get details about an async request
     v1       | fileset snapshot {id} browse | get    | Lists all files and directories in a given path
     v1       | fileset snapshot {id}        | get    | Get information for a fileset snapshot
     v1       | fileset {id} missed_snapshot | get    | Get missed snapshots for a fileset
     v1       | fileset {id} search          | get    | Search for a file within the fileset
     v1       | fileset {id}                 | get    | Get information for a single fileset
     v1       | fileset                      | get    | Get summary information for all filesets
     v1       | fileset_template {id}        | get    | Get information for a fileset template
     v1       | fileset_template             | get    | Get summary information for all fileset templates
    
    **Total amount of objects [13]
    ```
	
3. From the summary field I realize that the only commands that would  bring me information and details related to the fileset itself would be:
    ```
     v1       | fileset {id}                 | get    | Get information for a single fileset
     v1       | fileset                      | get    | Get summary information for all filesets
    ```

4. So I decide to check what are the details available in those API endpoints, with the following command:
    ```
    $ rbkcli fileset -s ?MAP
    [allowBackupHiddenFoldersInNetworkMounts]
    [allowBackupNetworkMounts]
    [arraySpec]
    [arraySpec][proxyHostId]
    [configuredSlaDomainId]
    [configuredSlaDomainName]
    [effectiveSlaDomainId]
    [effectiveSlaDomainName]
    [effectiveSlaDomainPolarisManagedId]
    [exceptions]
    [excludes]
    [hostId]
    [hostName]
    [id]
    [includes]
    [isPassthrough]
    [isRelic]
    [name]
    [operatingSystemType]
    [primaryClusterId]
    [shareId]
    [templateId]
    [templateName]
    [useWindowsVss]
    
    $ rbkcli fileset id -s ?MAP
    [allowBackupHiddenFoldersInNetworkMounts]
    [allowBackupNetworkMounts]
    [archiveStorage]
    [archivedSnapshotCount]
    [arraySpec]
    [arraySpec][proxyHostId]
    [backupScriptErrorHandling]
    [backupScriptTimeout]
    [configuredSlaDomainId]
    [configuredSlaDomainName]
    [effectiveSlaDomainId]
    [effectiveSlaDomainName]
    [effectiveSlaDomainPolarisManagedId]
    [exceptions]
    [excludes]
    [hostId]
    [hostName]
    [id]
    [includes]
    [isPassthrough]
    [isRelic]
    [localStorage]
    [name]
    [operatingSystemType]
    [postBackupScript]
    [preBackupScript]
    [primaryClusterId]
    [protectionDate]
    [shareId]
    [snapshotCount]
    [snapshots]
    [snapshots][archivalLocationIds]
    [snapshots][cloudState]
    [snapshots][consistencyLevel]
    [snapshots][date]
    [snapshots][expirationDate]
    [snapshots][fileCount]
    [snapshots][filesetName]
    [snapshots][id]
    [snapshots][indexState]
    [snapshots][isOnDemandSnapshot]
    [snapshots][replicationLocationIds]
    [snapshots][slaId]
    [snapshots][slaName]
    [snapshots][sourceObjectType]
    [templateId]
    [templateName]
    [useWindowsVss]
    ```
	
    I see then that the command "$ rbkcli fileset {id}" does provide me with the snapshot details, represented on the fields "[snapshots][archivalLocationIds]".
	
5. So now I need to figure out what does this command requires to run:
    ```
    $ rbkcli fileset id -i
    Description: [Retrieve summary information for a fileset by specifying the fileset ID.]
       Endpoint: [/v1/fileset/{id}]
    	 Method: [get]
     Parameters: [1]
    			 -id
    			   Description: Specify the fileset ID..
    			   Additional info: This parameter is REQUIRED to run and should be provided in the path as a string.
    ```

### How can I assemble my command?

The parameter required to run this command is the fileset ID. As a user, I could run this manually for all the filesets, but that would take too long... So I can use the "-l/--loop" parameter.
1. The "-l/--loop" parameter allows me to run an API endpoint and use a field from that to run another API endpoint. So the command to get details on all filesets would be:
    ```
    $ rbkcli fileset --loop id,hostName "fileset {id}"
    ```
    Effectively, in this command I am selecting the fields id and hostName from the json result of "rbkcli fileset" and using the id field in "{id}" as a parameter for "fileset {id}". **rbkcli** will take care of replacing the ids result by result for me.
    It will return one single json result with all the details. "-l/--loop" parameter will add the fields I provide (in this case id,hostName) to the final result with a prefix "loop_" in the name. 
    
2. From those details now I can select or cut the field I want.
    ```
    rbkcli fileset -l id,hostName "fileset/{id} -c snapshots"
    ```
    By adding "-c snapshots", I will then get only the content of the nested key snapshots plus the "loop_" fields as a result. The reason is that "-c/--context" parameter changes the context of the json output, by entering a nested key (a key inside a key).

3. Now I have a list of snapshots that contain all the data I need, to identify fileset snapshots that needs to be expired or reconfigured:
    ```
    $ rbkcli fileset -l id,hostName "fileset/{id} -c snapshots" -s date,loop_id,loop_hostName,archivalLocationIds\!=[] -T
    ```
    I then select the fields I want, filtering the "archivalLocationIds" that are not empty. Finally I convert the output into a table by adding "-T"

