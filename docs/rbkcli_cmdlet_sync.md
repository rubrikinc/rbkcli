# /rbkcli/cmdlet/sync
## Methods
### post
- **Description:** Applies cmdlets profiles to the target environment, use this when manually changing profiles.
- **Parameters:** No parameters are accepted.
- **Response:** Following is the json response structure, under properties are the fields which are returned:  
    1. OpenAPI description:
        ```json
        'responses': {
            '200': {
                'description': str('Returns status of the sync task.'),
                'schema': {
                    'CmdletSyncInfo': {
                        'properties': {
                            'result': {
                                'description': 'The result of the requested operation.',
                                'type': 'string'
                            }                                          
                        }
                    }
                }
            }
        },
        ```
    2. Response Example:
        ```
        {
          "result": "<value>"
        }
        ```
- **Usage:** It is used to synchronize the available cmdlets in the cmdlets profile with the commands that were imported by rbkcli.
    1. Example 1: Sync cmdlets.
        ```
        $ rbkcli cmdlet sync -m post
        {
          "result": "Applied cmdlets profile to environment configuration."
        }
        ```
