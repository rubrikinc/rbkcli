
# Complex commands
---
Very often when validating backups or troubleshooting issues, support engineers are required to get details of a sub-list of objects. In order to make that possible without the need of scripting, users can create **Complex commands**.
Such commands leverage **json output** manipulation with **Natural key assignment**, filtering results and looping it into another API.
To make sure you have the right background before exploring the **Complex commands** , visit the following:
 - [Natural key assignment](natural_key_assignment.md)
 - [JSON Output](json_output.md)
 
## Chain of thought
Once **rbkcli** is a dynamic CLI created from **Rubrik's** API Endpoints, its base commands are all APIs. API endpoints are created to facilitate structure data transfer, but never designed with human interaction as a priority.
Therefore in order to get specific details for a sub list of objects, users will need to understand **Rubrik's** data flow and organize their commands accordingly.
The following organization can help you get the data you need:
1 - Do I need information about object(s) or event(s)?
	Is the issue or situation you are investigating a failure, with a error or do you want to know how something is configured? 
	Usually the answer here is related to the reason why you are interacting with **Rubrik** system at this time.
2 - What are the commands available to get that type of information?
	After you are clear on what you are looking for, you can search for tools to get you there, the following command is your friend:
- For all available commands:
	```
	$ rbkcli commands -T
	```
 - To filter commands which contains keyword:
	```
	$ rbkcli commands -f endpoint~vmware -T
	```
3 - What is the available command capable of performing?
- You can discover this information by using the following parameters "-i/--info" and "-d/--documentation", such as:
	```
	$ rbkcli commands -i
	Description: [Retrieve a list of all the available commands on rbkcli, including all APIs imported.]
	   Endpoint: [/rbkcli/commands]
		 Method: [get]
	 Parameters: [0]
	```
- A more complex API endpoint with several query parameters accepted is:
	```
	$ rbkcli vmware vm -i
	Description: [Get summary of all the VMs]
	   Endpoint: [/v1/vmware/vm]
		 Method: [get]
	 Parameters: [11]
				 -effective_sla_domain_id
				   Description: Filter by ID of effective SLA Domain..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -primary_cluster_id
				   Description: Filter by primary cluster ID, or **local**..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -limit
				   Description: Limit the number of matches returned..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a integer.

				 -offset
				   Description: Ignore these many matches in the beginning..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a integer.

				 -is_relic
				   Description: Filter by the isRelic field of the virtual machine. When this parameter is not set, return both relic and non-relic virtual machines..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a boolean.

				 -name
				   Description: Search by using a virtual machine name..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -moid
				   Description: Search by using a virtual machine managed object ID..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -sla_assignment
				   Description: Filter by SLA Domain assignment type..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -guest_os_name
				   Description: Filters by the name of operating system using infix search..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -sort_by
				   Description: Sort results based on the specified attribute..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.

				 -sort_order
				   Description: Sort order, either ascending or descending..
				   Additional info: This parameter is NOT REQUIRED to run and should be provided in the query as a string.
	```
4 - What is the level of details provided by the command?
- You can easily see this by adding the "-s ?" or "-s ?MAP" parameter to the end of the command, such as:

	```
	$ rbkcli vmware vm -s ?MAP
	[agentStatus]
	[agentStatus][agentStatus]
	[agentStatus][disconnectReason]
	[cloudInstantiationSpec]
	[cloudInstantiationSpec][imageRetentionInSeconds]
	[clusterName]
	[configuredSlaDomainId]
	[configuredSlaDomainName]
	[effectiveSlaDomainId]
	[effectiveSlaDomainName]
	[effectiveSlaDomainPolarisManagedId]
	[effectiveSlaSourceObjectId]
	[effectiveSlaSourceObjectName]
	[folderPath]
	[folderPath][id]
	[folderPath][managedId]
	[folderPath][name]
	[guestCredentialAuthorizationStatus]
	[guestOsName]
	[hostId]
	[hostName]
	[id]
	[infraPath]
	[infraPath][id]
	[infraPath][managedId]
	[infraPath][name]
	[ipAddress]
	[isRelic]
	[isReplicationEnabled]
	[moid]
	[name]
	[parentAppInfo]
	[parentAppInfo][id]
	[parentAppInfo][isProtectedThruHierarchy]
	[powerStatus]
	[primaryClusterId]
	[protectionDate]
	[slaAssignment]
	[snapshotConsistencyMandate]
	[toolsInstalled]
	[vcenterId]
	[vmwareToolsInstalled]
	```
	
5 - With the available commands and details, what do I need?
- This is usually what takes longer, figuring out the end command that will bring you exactly what you need.
	Once you have that you can create your custom command to get the info you need, something similar to:
	```
	$ rbkcli vmware vm -f vcenterId=vCenter:::9445ca93-f4e1-4146-8562-930e32ef04ea,toolsInstalled=False -s moid,name -T
	```
	In this example, we are requesting all VMware VMs added to Rubrik environment, then we are filtering only VMs that are from a specific vCenter and do not have tools installed. 
	From that result we select moid, name of the VM and transform it to a table. We select that info so we can go to vCenter and install the necessary tool.
	

## Cases

Following are examples of **Complex commands** with a breakdown explanation of the parameters used:
 - [Get archived snapshots details from all filesets](complex_commands_1.md)
 - [Get details on all HDDs of the cluster - NR ](not_ready.md)
 - [Get all failed events related to VMware VMs on a specific date - NR ](not_ready.md)
 
Generally all **Cmdlets** are originally a complex commands. For examples of **Cmdlets** visit:
 - [Cmdlets](use_cmdlets.md)
