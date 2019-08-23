# Configuration File

Configurable options allows for minimal customization and workflow changes. The configuration file is written in json, therefore it has to be a valid file to be loaded. If the file is changed and it is not valid, **rbkcli** will recreate it with the default data.
Following are the available configuration parameters that are available in the previously mentioned configuration file (/home/<user>/rbkcli/conf/rbkcli.conf):

## blackList
* Description: List of APIs that will never be available through rbkcli module, no matter the user profile.
* Default value is an empty list: []
* Example of configuration in use:
	```json
	"blackList": {
		  "description": "",
		  "value": ["v1:/cluster/{id}/version:get:NA",
			"internal:/vmware/vm/snapshot/{id}:post:NA"]
		},
	```

## credentialsFile
* Description: File where to load credentials from, before looking for environmental variables.
* Default value is a string: "target.conf"
* Example of configuration in use:
	```json
	"credentialsFile": {
		  "description": "File where to load credentials from, before looking for env vars.",
		  "value": "target.conf"
		},
	```

## logLevel
* Description: Verbosity of the logs written to the file logs/rbkcli.log.
* Default value is a string: "debug"
* Example of configuration in use:
	```json
	"logLevel": {
		  "description": "Verbosity of the logs written to the file logs/rbkcli.log.",
		  "value": "debug"
		},
	```

## storeToken
* Description: Caches the last successful token with environment data.
* Default value is a string: "False"
* Example of configuration in use:
	```json
	"storeToken": {
		  "description": "Caches the last successful token with environment data.",
		  "value": "False"
		},
	```

## useCredentialsFile
* Description: Tries to load credentials from auth file before looking for env vars.
* Default value is a string: "False"
* Example of configuration in use:
	```json
	"useCredentialsFile": {
		  "description": "Tries to load credentials from auth file before looking for env vars.",
		  "value": "False"
		},
	```

## whiteList
* Description: List of APIs that will always be available through rbkcli module, no matter the user profile.
* Default value is an empty list: []
* Example of configuration in use:
	```json
	"whiteList": {
		  "description": "",
		  "value": ["internal:/session:post:NA"]
		}
	```
## userProfile
* Description: Each profile has different sets of APIs available to be called, it can be admin or support.
* Default value is a string: "admin"
* Example of configuration in use:
	```json
	"userProfile": {
		"description" : "String value which can be admin or support. A profile is a set of API endpoints that is available in the command line.",
		"value" : "admin"
	}
```