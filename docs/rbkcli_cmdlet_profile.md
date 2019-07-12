# /rbkcli/cmdlet/profile
## Methods
### get
- **Description:** 'Gets a list of all cmdlet's profiles in rbkcli.'.
- **Parameters:** No parameters are accepted.
- **Response:** Following is the json response structure, under properties are the fields which are returned:
    1. OpenAPI description:
        ```
        'responses': {
            '200': {
                'description': str('Returns a list of avail'
                                   'able cmdlets profiles'),
                'schema': {
                    'items': {
                        'CmdletsProfileInfo': {
                            'properties': {
                                'name': {
                                    'description': 'Name of the existing profile.',
                                    'type': 'string'
                                },
                                'path': {
                                    'description': 'Path to the existing profile.',
                                    'type': 'string'
                                },
                            }
                        }
                    }
                }
            }
        },
        ````
    2. Response Example:
        ```
        [
          {
            "name": "<value>",
            "path": "<value>"
          }
        ]
        ```
- **Usage:** It is used to see all existing cmdlet's profiles seen by rbkcli.
    1. Example 1: Get a raw list of all cmdlet's profiles.
        ```
        $ rbkcli cmdlet profile
        [
          {
            "name": "cmdlets",
            "path": "/home/bmanesco/rbkcli/conf/cmdlets/cmdlets.json"
          }
        ]
        ```

### post
- **Description:** Create a new cmdlet profile to rbkcli.
- **Parameters:** As a parameter you have to pass a single string, being either formatted as natural key assignment or as json string. Following is the description of the parameters:
    ```json
        'parameters': [
            {
            'name': 'name',
            'description': 'Name of the cmdlet profile to be created, the profile name will reflect in a file called <name>-cmdlets.json.',
            'in': 'body',
            'required': True,
            'type': 'string'
            }
        ]
    ```
- **Response:** Following is the json response structure, under properties are the fields which are returned:  
    1. OpenAPI description:
        ```json
        'responses': {
            '200': {
                'description': str('Returns status of the add task.'),
                'schema': {
                    'CmdletProfileCreationInfo': {
                        'properties': {
                            'result': {
                                'description': 'The result of the requested operation.',
                                'enum': [
                                    'Succeeded',
                                    'Failed'
                                ],
                                'type': 'string'
                            },
                            'message': {
                                'description': 'Message(s) explaining how was the execution of the requested operation.',
                                'type': 'array'
                            },
                            'data': {
                                'description': 'If operation succeeds, returns the created object.',
                                'type': 'json'
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
          "result": "<value>",
          "message": [
            "<value>",
            "<value>"
          ],
          "data": {
            "name": "<value>",
            "path": "<value>"
          }
        }
        ```
- **Usage:** It is used to create cmdlets profiles, which are portable to another rbkcli installation and holds the cmdlets records.
    1. Example 1: You can provide the required parameters for cmdlets creation as natural key assignment format once the only required parameter is name.
        ```
        $ rbkcli cmdlet profile -m post -p name=bmanesco
        {
          "result": "Succeeded",
          "message": [
            "Created profile successfully."
          ],
          "data": {
            "name": "bmanesco",
            "path": "/home/bmanesco/rbkcli/conf/cmdlets/bmanesco-cmdlets.json"
          }
        }
        ```
[Back to [Meta APIs](meta_apis.md)]