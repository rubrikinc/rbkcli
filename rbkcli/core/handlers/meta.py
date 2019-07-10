"""Meta commands module for rbkcli."""

import json
import os
from rbkcli.base import CONSTANTS, RbkcliException
from rbkcli.core.handlers import ApiTargetTools, RbkcliResponse

from rbkcli.core.handlers.cmdlets import CmdletsControls
from rbkcli.core.handlers.customizer import CustomizerControls


class MetaCmds(ApiTargetTools):
    """
    Class to provide Rbkcli meta commands.

    Any command related to changing or viewing the rbkcli environment will,
    come from here. This can be seen as the APIs of the rbkcli.
    It will be loaded with the API handlers and have the same methods:
    -import_api
    -execute_api
    -gen_authorization_lists

    Also will have same variables:
    -filter_list[]
    -focus_list

    So eventhough the instantiation is different, all the other actions,
    performed by the OperationsHandler will be supported, allowing is to deal
    with this as any other API, creating 2 layers of transparency:
    -cli wont know the difference
    -target wont know the difference.

    """

    def __init__(self, user_profile, base_kit):
        """Initialize Meta commands class."""
        ApiTargetTools.__init__(self, base_kit)

        self.user_profile = user_profile
        self.version = 'rbkcli'
        self.filter_lists = {}

        self.focus_list = []
        self.all_ops = []
        self.all_apis = {}

        self.meta_api = self.dot_dict()

        self._gen_docs()
        self._gen_exec_dict()
        self._gen_exec_api()

    def gen_authorization_lists(self):
        """
        Create custom lists of authorized based in the user profile.

        The focus list is used to verify if the API can be executed or not.
        """
        filter_list = self._create_all_methods_list(string='REQUIRES SUPPORT'
                                                    ' TOKEN')

        for user in CONSTANTS.USERS_PROFILE:
            self.filter_lists[user] = []
            requires = ''
            if user == 'admin':
                requires = 'NA'
            for method in CONSTANTS.SUPPORTED_USER_METHODS[user]:
                for method_line in filter_list:
                    if str(':%s:%s' % (method, requires)) in method_line:
                        self.filter_lists[user].append(method_line)

        for user, filter_list in self.filter_lists.items():
            filter_list.sort()

        self.focus_list = self.filter_lists[self.user_profile]

    def import_api(self):
        """Return the generated API doc for the meta commands."""
        return self.meta_api.doc

    def execute_api(self, *args, **kwargs):
        """Execute method based in the endpoint and method entered."""
        method, endpoint = args
        if '?' in endpoint:
            endpoint, query = endpoint.split('?')
        else:
            query = ''

        endpoint = self.meta_api.exec_['paths']['/' + endpoint]

        return endpoint[method]['exec_fn'](kwargs)

    def _gen_exec_dict(self):
        """Generate translation between endpoints and public methods."""
        self.meta_api.exec_dict = {
            'commands_get': self.ops_commands_get,
            'jsonfy_get': self.ops_jsonfy_get,
            ##TEST
            'cmdlet_get': self.ops_cmdlets_get,
            'cmdlet_post': self.ops_cmdlets_post,
            'cmdlet_profile_get': self.ops_cmdlets_profile_get,
            'cmdlet_profile_post': self.ops_cmdlets_profile_post,
            'cmdlet_sync_post': self.ops_cmdlets_sync_post,
            'cmdlet_delete': self.ops_cmdlets_delete,
            'script_sync_post': self.ops_scripts_sync_post,
            'script_get': self.ops_scripts_get
        }

    def _gen_exec_api(self):
        """Apply public method to dictionary with endpoint documentation."""
        # FIX this.
        self.meta_api.exec_ = self.tools.cp_dict(self.meta_api.doc)
        for method, method_fn in self.meta_api.exec_dict.items():
            path = method.strip().split('_')
            api_method = path[-1]
            path.pop(-1)
            path = '/' + '/'.join(path)
            try:
                path_dict = self.meta_api.exec_['paths'][path]
                path_dict[api_method]['exec_fn'] = method_fn
                self.meta_api.exec_['paths'][path] = path_dict
            except KeyError:
                pass

    def _gen_docs(self):
        """Create static API documentation and store to class var."""
        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.
        self.meta_api.doc = {
            'definitions': {},
            'paths': {
                '/commands': {
                    'get': {
                        'description': str('Retrieve a list of all the '
                                           'available commands on rbkcli, '
                                           'including all APIs imported.'),
                        'operationId': 'queryAvailableCommands',
                        'parameters': [],
                        'responses': {
                            '200': {
                                'description': str('Returns a list of avail'
                                                   'able commands'),
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
                                                    'type': 'string'
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
                        'summary': 'List available commands',
                        'tags': [
                            '/commands'
                        ],
                        'x-group': 'commands'
                    }
                },
                ##TEST
                '/cmdlet': {
                    'get': {
                        'description': 'Gets a list of all cmdlets in rbkcli.',
                        'operationId': 'queryCmdlets',
                        'parameters': [],
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
                                                    'description': 'Parameter to replace in the commads, provided in a comma separated list.',
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
                        'summary': 'List available cmdlets.',
                        'tags': '',
                        'x-group': ''
                    },
                    'delete': {
                        'description': 'Removes cmdlet from rbkcli permanently',
                        'operationId': 'removeCmdlet',
                        'parameters': [
                            {
                            'name': 'id',
                            'description': 'Id(s) of the cmdlet that will be deleted.',
                            'in': 'body',
                            'required': True,
                            'type': 'string/array'
                            }
                        ],
                        'responses': {
                            '200': {
                                'description': str('Returns status of the removal task.'),
                                'schema': {}
                                }
                        },
                        'summary': 'Remove cmdlet.',
                        'tags': '',
                        'x-group': ''
                    },                    
                    'post': {
                        'description': 'Add a new cmdlet to rbkcli',
                        'operationId': 'addCmdlet',
                        'parameters': [],
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
                                                'description': 'Message(s) explainning how was the execution of the requested operation.',
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
                        'summary': 'Add new cmdlet to rbkcli',
                        'tags': '',
                        'x-group': ''
                    }                    
                },
                ##TEST
                '/cmdlet/profile': {
                    'get': {
                        'description': 'Gets a list of all cmdlets profiles in rbkcli',
                        'operationId': 'queryCmdletProfile',
                        'parameters': [],
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
                        'summary': 'List cmdlet\'s profiles',
                        'tags': '',
                        'x-group': ''
                    },
                    'post': {
                        'description': 'Create a new cmdlet profile to rbkcli',
                        'operationId': 'addCmdletProfile',
                        'parameters': [
                            {
                            'name': 'name',
                            'description': 'Name of the cmdlet profile to be created, the profile name will reflect in a file called <name>-cmdlets.json.',
                            'in': 'body',
                            'required': True,
                            'type': 'string'
                            }
                        ],
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
                                                'description': 'Message(s) explainning how was the execution of the requested operation.',
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
                        'summary': 'Create cmdlet profile.',
                        'tags': '',
                        'x-group': ''
                    }
                                        
                },
                ##TEST
                '/cmdlet/sync': {
                    'post': {
                        'description': 'Applies cmdlets profiles to the target environment, use this when manually changing profiles.',
                        'operationId': 'applyCmdletProfile',
                        'parameters': [],
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
                        'summary': 'Apply cmdlets changes to target environment.',
                        'tags': '',
                        'x-group': ''
                    },              
                },
                ##TEST
                '/script': {
                    'get': {
                        'description': 'Gets a list of all valid scripts in rbkcli/scripts folder.',
                        'operationId': '',
                        'parameters': [],
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
                        'summary': 'List scripts available to be used in rbkcli.',
                        'tags': '',
                        'x-group': ''
                    },              
                },    
                ##TEST
                '/script/sync': {
                    'post': {
                        'description': 'Imports all child classes of RbkcliBlackOps in scripts files in rbkcli',
                        'operationId': '',
                        'parameters': [],
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
                        'summary': 'Import operations created in a external script.',
                        'tags': '',
                        'x-group': ''
                    },              
                },                     
                ##TEST
                '/jsonfy': {
                    'get': {
                        'description': 'Loads a json file or string, return json result which allows for system manipulation.',
                        'operationId': 'loadJsonFile',
                        'parameters': [
                            {
                            'name': 'file',
                            'description': 'Path to the json file to be loaded.',
                            'in': 'body',
                            'required': True,
                            'type': 'string'
                            },
                            {
                            'name': '<any_keys>',
                            'description': 'Enter any key as natural key assignment or string Json.',
                            'in': 'body',
                            'required': True,
                            'type': 'string'
                            }
                        ],
                        'responses': {
                            '200': {
                                'description': str('Returns a list of avail'
                                                   'able commands'),
                                'schema': {}
                                }
                        },
                        'summary': 'Loads provided json file.',
                        'tags': '',
                        'x-group': ''
                    }
                }
            }
        }

    def _create_all_methods_list(self, field='summary', string='TOKEN'):
        """Create a list of all defined methods for meta commands."""
        filter_list = []
        string_ = string.replace(' ', '_')

        for endpoint, endpoint_data in self.meta_api.doc['paths'].items():
            for method, method_data in endpoint_data.items():
                filter_list.append('%s:%s:%s:%s' % (self.version, endpoint,
                                                    method, 'NA'))
                for doc_field, doc_field_data in method_data.items():
                    if field == doc_field and string in doc_field_data:
                        filter_list.remove('%s:%s:%s:%s' % (self.version,
                                                            endpoint,
                                                            method, 'NA'))
                        filter_list.append('%s:%s:%s:%s' % (self.version,
                                                            endpoint,
                                                            method, string_))
        self.endpoints = self.meta_api.doc
        return filter_list

    @RbkcliResponse.successfull_response
    def ops_commands_get(self, kwargs):
        """
        Retrieve a list of all the available commands on rbkcli.

        Including all APIs imported.
        """
        params = kwargs['params']
        result_dict = []
        commands_table = ['']
        headers = ['version', 'endpoint', 'method', 'summary']

        if params != '':
            params = params.split(' ')
            params = '/'.join(params)
            for ops in self.all_ops:
                if params in ops:
                    result_dict.append(self._generate_op_json(ops))
        else:
            for ops in self.all_ops:
                result_dict.append(self._generate_op_json(ops))

        if result_dict != []:
            summary = 'Number of commands found'
            commands_ops = self.json_ops()
            commands_table = commands_ops.simple_dict_table(result_dict,
                                                            headers=headers,
                                                            summary=summary)

        return json.dumps(result_dict, indent=2)


    @RbkcliResponse.successfull_response
    def ops_jsonfy_get(self, kwargs):
        """rbkcli jsonfy operation, convert str to json."""
        params = kwargs['params']
        data = kwargs['data']
        result_dict_keys = []

        try:
            result_dict = json.loads(data)
            if isinstance(result_dict, dict):
                result_dict_keys = list(result_dict.keys())

            if result_dict_keys == ['file']:
                with open(result_dict['file'], 'r') as f:
                    result_dict = json.load(f)
        except Exception as e:
            result_dict = {
                'result': 'Failed',
                'message': 'jsonfy failed to parse with: ' + str(e),
                'data': str(data)
            }

            
        return json.dumps(result_dict, indent=2)

    @RbkcliResponse.successfull_response
    def ops_cmdlets_get(self, kwargs):
        """rbkcli cmdlets operation, list available cmdlets."""
        return CmdletsControls(self.tools).list_cmdlets(kwargs)

    @RbkcliResponse.successfull_response
    def ops_cmdlets_sync_post(self, kwargs):
        """rbkcli cmdlets sync operation, apply changes to cmdlets."""
        kwargs['target_folder'] = self.base_kit.target_folder
        return CmdletsControls(self.tools).sync_cmdlets(kwargs)

    @RbkcliResponse.successfull_response
    def ops_scripts_sync_post(self, kwargs):
        """rbkcli scripts sync operation, apply changes to scripts."""
        kwargs['target_folder'] = self.base_kit.target_folder
        return CustomizerControls(self.tools).sync_scripts(kwargs)

    @RbkcliResponse.successfull_response
    def ops_scripts_get(self, kwargs):
        """rbkcli scripts operation, list available scripts."""
        kwargs['target_folder'] = self.base_kit.target_folder
        return CustomizerControls(self.tools).list_scripts(kwargs)

    @RbkcliResponse.successfull_response
    def ops_cmdlets_post(self, kwargs):
        """rbkcli cmdlets create operation."""
        kwargs['target_folder'] = self.base_kit.target_folder
        return CmdletsControls(self.tools).add_cmdlet(kwargs)
    
    @RbkcliResponse.successfull_response
    def ops_cmdlets_delete(self, kwargs):
        """rbkcli cmdlets delete operation."""
        kwargs['target_folder'] = self.base_kit.target_folder
        return CmdletsControls(self.tools).remove_cmdlet(kwargs)

    @RbkcliResponse.successfull_response
    def ops_cmdlets_profile_get(self, kwargs):
        """rbkcli cmdlets profile operation, list available profiles."""
        return CmdletsControls(self.tools).list_cmdlets_profiles(kwargs)

    @RbkcliResponse.successfull_response
    def ops_cmdlets_profile_post(self, kwargs):
        """rbkcli cmdlets profile create operation."""
        return CmdletsControls(self.tools).add_cmdlet_profile(kwargs)

    def _generate_op_json(self, ops):
        """Generate the json of the available commands for the target."""
        version, endpoint, method, comment = ops.split(':')
        del comment
        endpoint_cmd = endpoint.split('/')
        endpoint_cmd = ' '.join(endpoint_cmd[1:])
        paths = self.all_apis[version]['paths']
        try:
            op_dict = {
                'version': version,
                'endpoint': endpoint_cmd,
                'method': method,
                'summary': str(paths[endpoint][method]['summary'])
            }
        except KeyError as error:
            msg = str('Unable to load meta command [%s]. There is a mismatch'
                      ' between cached version and source code.' % str(error))
            raise RbkcliException.ClusterError(msg)

        return op_dict

    def store_all_ops(self, ops):
        """Store all operations in intance variable, stetic reason."""
        self.all_ops = ops
