# /rbkcli/script/sync
## Methods
### post
- **Description:** Imports all child classes of RbkcliBlackOps in scripts files in rbkcli.
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
- **Usage:** It is used to synchronize the available scripts in the cmdlets folder, importing it along with the commands that were imported by rbkcli already.
    1. Example 1: Sync scripts.
        ```
        $ rbkcli script sync -m post
        {
          "result": "Applied scripts to environment configuration."
        }
        ```
[Back to [Meta APIs](meta_apis.md)]