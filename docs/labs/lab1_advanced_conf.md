# ADVANCED CONFIGURATION / HACKS

1. Change rbkcli to support mode:
	```
	$ rbkcli commands -T
	```
	
	Change the file
	
	```
	$ vi ~/rbkcli/conf/rbkcli.conf

	"userProfile": {
      "description": "String value which can be admin or support. A profile is a set of API endpoints that is available in the command line.",
      "value": "support"

	```
	
	Check commands again:
	
	```
	$ rbkcli commands -T
	```

2. Use GUI to create new SLA:
	- Use devtools on Chrome and capture payload passed by UI:
        ```
        {"name":"TEST","frequencies": [{"hourly":{"frequency":24,"retention":2},"daily":{"frequency":7,"retention":4}],"logConfig":{},"allowedBackupWindows":[{"startTimeAttributes":{"minutes":30,"hour":20},"durationInHours":3}],"firstFullAllowedBackupWindows":[],"archivalSpecs":[],"replicationSpecs":[],"showAdvancedUi":true,"advancedUiConfig":[{"timeUnit":"Hourly","retentionType":"Daily"},{"timeUnit":"Daily","retentionType":"Weekly"}],"isRetentionLocked":false}
        ```
	
	- Save this to a file:
        ```
        vi agressive_sla_model.json
        ```

3. List all available SLAs:
	```
	rbkcli sla_domain -s id,name -T
	```

4. Use the file to create SLA with rbkcli:
	- test if rbkcli can read the file as json:
        ```
        rbkcli jsonfy -p file=/tmp/agressive_sla_model.json -s name
        ```
	
	- Save the contents of the file into a bash variable:
        ```
        agressive_sla=$(cat /tmp/agressive_sla_model.json)
        ```
	
	- Run the API to create the SLA:
        ```
        $ rbkcli sla_domain -m post -p $agressive_sla -v v2
        ```
	
	- Verify if the new SLA has been created:
        ```
        $ rbkcli sla_domain -v v2 -s id,name -T
         id                                   | name
        ================================================
         d9c5fac4-cc7a-41b6-ae54-5f9b8bfb6ae0 | Bronze
         e3b64843-fed9-415d-b1d5-1735c3ce906c | Gold
         36350129-c275-494a-a8b9-24d01a5830db | 24Hours
         e50b43e3-27af-431d-b8dc-6a54d9572fdb | Silver
         490c2e1f-1d8f-4a61-90d0-b7c5e5f09a5f | TEST
    
        **Total amount of objects [5]
    
        ```
	
5. Remove the TEST one created on the UI.
	- Get the ID of the SLA you want to delete
        ```
        $ rbkcli -v v2 sla_domain -s id,name~TEST
        [
          {
            "id": "490c2e1f-1d8f-4a61-90d0-b7c5e5f09a5f",
            "name": "TEST"
          }
        ]
    
        ```
	
	- Delete it:
        ```
        $ rbkcli -v v2 sla_domain 490c2e1f-1d8f-4a61-90d0-b7c5e5f09a5f -m delete
        Response code: 204
        Response text:
    
        ```


<-- Back to [Useful learning workflows](labs.md)