# /rbkcli/commands
The "commands" endpoint is used to list all the APIs that were import by rbkcli. It creates a unified list of objects returned as a JSON by default. Use the JSON customization arguments to filter the list and find the API you want.
## Methods
### get
- **Description:** Retrieve a list of all the available commands on rbkcli, icluding all APIs imported.
- **Parameters:** No parameters are accepted.
- **Response:** Following is the json response structure, under properties are the fields which are returned:
    1. OpenAPI description:
        ```json
        'responses': {
            '200': {
                'description': str('Returns a list of available commands'),
                'schema': {
                    'items': {
                        'CommandsInfo': {
                            'properties': {
                                'version': {
                                    'description': 'Version which the imported endpoint belongs to.',
                                    'type': 'string'
                                },
                                'endpoint': {
                                    'description': 'The API callable path, or API name.',
                                    'type': 'string'
                                },                                           
                                'method': {
                                    'description': 'Available method to call the API endpoint.',
                                    'type': 'array'
                                },
                                'summary': {
                                    'description': 'Short description of the action perfromed when Endpoint and method are called.',
                                    'type': 'string'
                                },                                               
                            }
                        }
                    }
                },
                'table_order': ['version', 'endpoint', 'method', 'summary']
            }
        },
        ```
    2. Response Example:
        ```
        [
          {
            "version": "<value>",
            "endpoint": "<value>",
            "method": "<value>",
            "summary": "<value>"
          }
        ]
        ```
- **Usage:** As commands output is quite simple, not containning any nested json, usually a couple of simple filters would suffice to narrow down the results:
    Example: Get commands related to "vmware" and "snapshots":
    ```
    ~$ rbkcli commands --filter endpoint~"vmware" --filter endpoint~"snapshot" -T
     endpoint                           | method | summary                                     | version
    ======================================================================================================
     vmware vm live_snapshot count {id} | get    | Count of all the live snapshots of a VM     | internal
     vmware vm snapshot count           | get    | Get a count of snapshots                    | internal
     vmware vm snapshot mount count     | get    | Get a count of live mounts                  | internal
     vmware vm snapshot mount {id}      | get    | Get summary information for a live mount    | internal
     vmware vm snapshot mount           | get    | Get summary information for all live mounts | internal
     vmware vm snapshot mount {id}      | get    | Get information for a Live Mount            | v1
     vmware vm snapshot mount           | get    | Get Live Mount information                  | v1
     vmware vm snapshot {id} browse     | get    | List files in VM snapshot                   | v1
     vmware vm snapshot {id}            | get    | Get VM snapshot details                     | v1
     vmware vm {id} missed_snapshot     | get    | Get details about missed snapshots for a VM | v1
     vmware vm {id} snapshot            | get    | Get list of snapshots of VM                 | v1
    
    **Total amount of objects [11]
    ```
  