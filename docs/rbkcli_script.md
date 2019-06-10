# /rbkcli/script
## Methods
### get
- **Description:** Gets a list of all valid scripts in rbkcli/scripts folder.
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
                        'ScriptsInfo': {
                            'properties': {
                                'module': {
                                    'description': 'Name of the script, also referred to as Python importable module.',
                                    'type': 'string'
                                },
                                'file': {
                                    'description': 'Path to the existing script file.',
                                    'type': 'string'
                                },
                                'class_name': {
                                    'description': 'Name of the existing child class of RbkcliBlackOps, which will become a command.',
                                    'type': 'string'
                                },
                                'endpoint': {
                                    'description': 'The callable command referring to the class_name.',
                                    'type': 'string'
                                },
                                'method': {
                                    'description': 'Method to call the script.',
                                    'type': 'string'
                                }
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
            "module": "<value>",
            "file": "<value>",
            "class_name": "<value>",
            "endpoint": "<value>",
            "method": "<value>"
          }
        ]
        ```
- **Usage:** It is used to see all existing classes inside scripts under folder ~/rbkcli/scripts/ and its subfolders, classes importable by rbkcli.
    1. Example 1: Get a raw list of all RbkcliBlackOps child classes.
        ```
        $ rbkcli script
        [
          {
            "module": "my_script",
            "file": "/home/bmanesco/rbkcli/scripts/my_script.py",
            "class_name": "MyOperation",
            "endpoint": "/mssql/snap/stats",
            "method": "get"
          }
        ]
        ```