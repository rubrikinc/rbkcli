# /rbkcli/cmdlet
## Methods
### get
- **Description:** 'Gets a list of all cmdlets in rbkcli.'.
- **Parameters:** No parameters are accepted.
- **Response:** Following is the json response structure, under properties are the fields which are returned:
    1. OpenAPI description:
        ```
        'responses': {
            '200': {
                'description': str('Returns a list of avail'
                                   'able cmdlets'),
                'schema': {
                    'items': {
                        'CmdletsInfo': {
                            'properties': {
                                'cmdlet_description': {
                                    'description': 'Description of the cmdlet being added',
                                    'type': 'string'
                                },
                                'cmdlet_summary': {
                                    'description': 'Short description of cmdlet being added',
                                    'type': 'string'
                                },                                           
                                'command': {
                                    'description': 'List of rbkcli existing commands which the cmdlet will trigger, each command can have a "<parameter>" entry which will be replaced by the parameter provided',
                                    'type': 'array'
                                },
                                'id': {
                                    'description': 'Auto generated UUID version 4 stored with the cmdlet',
                                    'type': 'string'
                                },
                                'multiple_output': {
                                    'description': 'Format of the json output of multiple commands triggered, segmented per command triggered or combined in one json.',
                                    'enum': [
                                        'segmented',
                                        'combined'
                                    ],
                                    'type': 'string'
                                },
                                'name': {
                                    'description': 'The display name of the cmdlet, which will be used to call it.',
                                    'type': 'string'
                                },   
                                'param': {
                                    'description': 'Parameter to replace in the commands, provided in a comma separated list.',
                                    'type': 'string'
                                },
                                'profile': {
                                    'description': 'Name of the file where the cmdlets are saved, default is cmdlets.json',
                                    'type': 'string'
                                },
                                'response_description': {
                                    'description': 'Description of the json response returned by the cmdlet.',
                                    'type': 'string'
                                },
                                'status': {
                                    'description': 'Result of a verification of all cmdlets names, if is duplicated the cmdlet wont\'t be usable and will be flagged as duplicated.',
                                    'enum': [
                                        'usable',
                                        'duplicated'
                                    ],
                                    'type': 'string'
                                },                                               
                            }
                        }
                    }
                },
                'table_order': ['profile','status','cmdlet','cmdlet_summary','multiple_output']
            }
        },
        ````
    2. Response Example:
        ```
        [
          {
            "cmdlet_description": "<value>",
            "cmdlet_summary": "<value>",
            "command": [
              "<value>",
              "<value>"
            ],
            "id": "<value>",
            "multiple_output": "<value>",
            "name": "<value>",
            "param": "<value>,<value>",
            "profile": "<value>.json",
            "response_description": "<value>",
            "status": "<value>"
          }
        ]

        ```
- **Usage:** It is used to see all existing cmdlets in all cmdlets profile, even if not imported as a command.
    1. Example 1: Get a raw list of all cmdlets.
        ```
        $ rbkcli cmdlet
        [
          {
            "cmdlet_description": "",
            "cmdlet_summary": "Retrieves a list of VMs in Silver SLA",
            "command": [
              "vmware vm -f effectiveSlaDomainName~Silver --loop id \"vmware vm {id}\" -c snapshots"
            ],
            "id": "e6d131a8-7d3b-42d2-a34a-8be19e0897d3",
            "multiple_output": "segmented",
            "name": "DemoCmdlet silver_vms",
            "param": "",
            "profile": "cmdlets.json",
            "response_description": "",
            "status": "usable"
          },
          {
            "cmdlet_description": "",
            "cmdlet_summary": "Retrieves a list of VMs in Bronze SLA",
            "command": [
              "vmware vm -f effectiveSlaDomainName~Bronze --loop id \"vmware vm {id}\" -c snapshots"
            ],
            "id": "199d77c5-5de5-46b9-8004-69bc8732abee",
            "multiple_output": "segmented",
            "name": "DemoCmdlet bronze_vms",
            "param": "",
            "profile": "cmdlets.json",
            "response_description": "",
            "status": "usable"
          }
        ]
        ```
    
    2. Example 2: Select the relevant fields and create a table.
        ```
        $ rbkcli cmdlet -s name,profile,status,cmdlet_summary,command -T
         name                  | profile      | status | cmdlet_summary                        | command
        ================================================================================================================================================================================
         DemoCmdlet silver_vms | cmdlets.json | usable | Retrieves a list of VMs in Silver SLA | ['vmware vm -f effectiveSlaDomainName~Silver --loop id "vmware vm {id}" -c snapshots']
         DemoCmdlet bronze_vms | cmdlets.json | usable | Retrieves a list of VMs in Bronze SLA | ['vmware vm -f effectiveSlaDomainName~Bronze --loop id "vmware vm {id}" -c snapshots']
        
        **Total amount of objects [2]
        ```
### post
- **Description:** Adds a new cmdlet to rbkcli and syncs the profiles.
- **Parameters:** As a parameter you have to pass a single string, being either formatted as natural key assignment or as json string. If the key passed is "file", then instead of loading the string **jsonfy** will attempt to load the json file. Following is the description of the parameters:
    ```json
    'parameters': [
        {
        'name': 'cmdlet_description',
        'description': 'Description of the cmdlet being added.',
        'in': 'body',
        'required': False,
        'type': 'string'
        },
        {
        'name': 'cmdlet_summary',
        'description': 'Short description of cmdlet being added',
        'in': 'body',
        'required': False,
        'type': 'string'
        },
        {
        'name': 'command',
        'description': 'List of rbkcli existing commands which the cmdlet will trigger, each command can have a "<parameter>" entry which will be replaced by the parameter provided',
        'in': 'body',
        'required': True,
        'type': 'array/string'
        },
        {
        'name': 'multiple_output',
        'description': 'Format of the json output of multiple commands triggered, segmented per command triggered or combined in one json.',
        'enum': [
            'segmented',
            'combined'
        ],
        'in': 'body',
        'required': False,
        'type': 'string'
        },
        {
        'name': 'name',
        'description': 'The display name of the cmdlet, which will be used to call it.',
        'in': 'body',
        'required': True,
        'type': 'string'
        },
        {
        'name': 'param',
        'description': 'Parameter to replace in the commands, provided in a comma separated list.',
        'in': 'body',
        'required': False,
        'type': 'string'
        },
        {
        'name': 'profile',
        'description': 'Name of the file where the cmdlets are saved, default is cmdlets.json.',
        'in': 'body',
        'required': True,
        'type': 'string'
        },
        {
        'name': 'response_description',
        'description': 'Description of the json response returned by the cmdlet.',
        'in': 'body',
        'required': False,
        'type': 'string'
        },
    ],
    ```
- **Response:** Following is the json response structure, under properties are the fields which are returned:  
    1. OpenAPI description:
        ```json
        'responses': {
            '200': {
                'description': str('Returns status of the add task.'),
                'schema': {
                    'CmdletCreationInfo': {
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
          "cmdlet_to_add": {
            "id": "<value>",
            "profile": "<value>",
            "name": "<value>",
            "cmdlet_summary": "<value>",
            "cmdlet_description": "<value>",
            "command": [
              "<value>",
              "<value>"
            ],
            "multiple_output": "<value>",
            "param": "<value>",
            "response_description": "<value>"
          }
        }
        ```
- **Usage:** It is used to create documented cmdlets, which are pointers to one or more existing rbkcli commands. By doing so, the user ends up customizing the commands available in rbkcli.
    1. Example 1: You can provide the required parameters for cmdlets creation as natural key assignment format when destination command is simple.
        ```
        $ rbkcli cmdlet -m post -p 'name=bronze_vms,profile=cmdlets.json,command=vmware vm -f effectiveSlaDomainName~Bronze'
        {
          "result": "Succeeded",
          "message": [],
          "cmdlet_to_add": {
            "id": "e12a0731-a29b-4c9a-90c6-e32752fe017f",
            "profile": "cmdlets.json",
            "name": "bronze_vms",
            "cmdlet_summary": "",
            "cmdlet_description": "",
            "command": [
              "vmware vm -f effectiveSlaDomainName~Bronze"
            ],
            "multiple_output": "segmented",
            "param": "",
            "response_description": ""
          }
        }
        ```
    2. Example 2: You can provide the required parameters for cmdlets creation as json string format, when the destination command is complex and have several arguments or you have multiple commands as destination.
        ```
        $ rbkcli cmdlet -m post -p '{"name": "vm snaps","profile": "cmdlets.json", "command": ["vmware vm -f effectiveSlaDomainName~Bronze --loop id \"vmware vm {id}\" -c snapshots"]}'
        {
          "result": "Succeeded",
          "message": [],
          "cmdlet_to_add": {
            "id": "de0a07bb-5c12-427b-9bdc-3660865ce102",
            "profile": "cmdlets.json",
            "name": "vm snaps",
            "cmdlet_summary": "",
            "cmdlet_description": "",
            "command": [
              "vmware vm -f effectiveSlaDomainName~Bronze --loop id \"vmware vm {id}\" -c snapshots"
            ],
            "multiple_output": "segmented",
            "param": "",
            "response_description": ""
          }
        }
        ```
### delete
- **Description:** Removes cmdlet from rbkcli permanently.
- **Parameters:** As a parameter you have to pass a single string, being either formatted as natural key assignment or as json string.
    ```json
   'parameters': [
        {
        'name': 'id',
        'description': 'Id(s) of the cmdlet that will be deleted.',
        'in': 'body',
        'required': True,
        'type': 'string/array'
        }
    ],
    ```
- **Response:** Following is the json response structure, under properties are the fields which are returned:  
    1. OpenAPI description:
        ```json
        'responses': {
            '200': {
                'description': str('Returns status of the add task.'),
                'schema': {
                    'CmdletCreationInfo': {
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
                                'description': 'If operation succeeds, returns the deleted object.',
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
            "id": "<value>",
            "profile": "<value>",
            "name": "<value>",
            "cmdlet_summary": "<value>",
            "cmdlet_description": "<value>",
            "command": [
              "<value>",
              "<value>"
            ],
            "multiple_output": "<value>",
            "param": "<value>",
            "response_description": "<value>"
          }
        }
        ```
- **Usage:** It is used to delete documented cmdlets.
    1. Example 1: You can provide the required parameters for cmdlets deletion as natural key assignment format once only one parameter is required.
        ```
        $ rbkcli cmdlet -m delete -p id=4f6af2d2-28ba-4635-81c3-f6b22f61f2e0
        [
          {
            "result": "Succeeded.",
            "message": "Found the following cmdlets with the provided ID(s).",
            "data": {
              "cmdlet_description": "",
              "cmdlet_summary": "",
              "command": [
                "vmware vm -f effectiveSlaDomainName~Bronze --loop id \"vmware vm {id}\" -c snapshots"
              ],
              "id": "4f6af2d2-28ba-4635-81c3-f6b22f61f2e0",
              "multiple_output": "segmented",
              "name": "vm snaps",
              "param": "",
              "profile": "cmdlets.json",
              "response_description": ""
            }
          }
        ]
        ```
[Back to [Meta APIs](meta_apis.md)]