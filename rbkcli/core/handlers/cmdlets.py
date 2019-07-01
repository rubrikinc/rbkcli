"""Meta commands module for rbkcli."""

import os
import json
import copy
from rbkcli.base import CONSTANTS, RbkcliException
from rbkcli.core.handlers import ApiTargetTools, RbkcliResponse
from rbkcli.core.handlers.callback import CallBack


class Cmdlets(ApiTargetTools):
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
        self.version = 'cmdlets'
        self.filter_lists = {}

        self.focus_list = []
        self.all_ops = []
        self.all_apis = {}

        self.meta_api = self.dot_dict()
        ## This class should not read the file every run, only when importing new API.
        ## Structural changes needed: gen_authorization_lists
        ### So the following 3 fn will have toi be adjusted

        #self._gen_docs()

    def gen_authorization_lists(self):
        """
        Create custom lists of authorized based in the user profile.

        The focus list is used to verify if the API can be executed or not.
        """
        #print(self.endpoints)

        #self._gen_docs()
        self.meta_api.doc = self.endpoints
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
        self._gen_docs()
        return self.meta_api.doc

    @RbkcliResponse.successfull_response
    def execute_api(self, *args, **kwargs):
        """Execute method based in the endpoint and method entered."""
        method, endpoint = args
        ## TEST
        #print(args)
        #print(kwargs)
        #del kwargs
        if '?' in endpoint:
            endpoint, query = endpoint.split('?')
        else:
            query = ''

        endpoint = self.meta_api.doc['paths']['/' + endpoint]

        last_command = {}
        last_command_ = []

        if len(endpoint[method]['operation']) > 1:
            flag_several = True
        else:
            flag_several = False

        for ops in enumerate(endpoint[method]['operation']):
            opers = self._assign_parameters(ops[1], kwargs['data'], endpoint[method]['parameters'])
            if flag_several:
                this_result = self.cbacker.call_back(opers)
                if endpoint[method]['responses']['200']['multiple_output'] == 'segmented':
                    last_command['comand_'+str(ops[0])] = self._load_json(this_result)
                elif endpoint[method]['responses']['200']['multiple_output'] == 'combined':
                    my_result = self._load_json(this_result)
                    if isinstance(my_result, dict):
                        
                        last_command_.append(my_result)
                    elif isinstance(my_result, list):
                        for item in my_result:
                            last_command_.append(item)

                    #if isinstance(my_result, dict):
                    #    for key, value in my_result.items():
                    #        last_command[key] = value
                    #elif isinstance(my_result, list):
                    #    last_command['comand_'+str(ops[0])] = my_result
            else:
                this_result = self.cbacker.call_back(opers)
                last_command = self._load_json(this_result)

        if last_command_ != []:
            last_command = last_command_

        return json.dumps(last_command, indent=2)
        #return endpoint[method]['exec_fn'](kwargs)

    def _assign_parameters(self, oper, entered_param, existing_param):
        if entered_param == {}:
            entered_param = '{}'
        entered_param = json.loads(entered_param)

        for key, value in entered_param.items():
            for expected_param in existing_param:

                param_name = expected_param['name']
                param_name = param_name.split(',')
                for p_name in param_name:
                    if key == p_name:
                        oper = oper.replace('<' + key + '>', value)

        return oper

    def _load_json(self, json_data):
        result = {}
        try:
            result = json.loads(json_data.text)
        except Exception as e:
            result['string_return'] = json_data.text

        return result

    def _get_cmdlets_files(self):
        cmdlets_files = []
        self.cmdlets_folder = CONSTANTS.CONF_FOLDER + '/cmdlets'
        try:
            cmdlets_folder = list(os.listdir(self.cmdlets_folder))
            for file in cmdlets_folder:
                if file.endswith('cmdlets.json'):
                    cmdlets_files.append(file)
        except Exception as e:
            return []
        return cmdlets_files

    def _load_cmdlets_files(self, cmdlets_files):
        loaded_cmdlets = []
        for file in cmdlets_files:
            loaded_cmdlets = loaded_cmdlets + self.tools.load_json_file(self.cmdlets_folder+'/'+file)
        return loaded_cmdlets
    
    def _get_usable_cmdlets(self, loaded_cmdlets):
        usable_cmdlets = []
        usable_cmdlets_list = []
        existing_cmdlets = copy.deepcopy(loaded_cmdlets)
        for item in enumerate(existing_cmdlets):
            if item[1]['name'] in usable_cmdlets_list:
                #loaded_cmdlets.remove(item[0])
                pass
            else:
                usable_cmdlets_list.append(item[1]['name'])
                usable_cmdlets.append(item[1])

        return usable_cmdlets


    def _gen_docs(self):
        """Create static API documentation and store to class var."""
        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.
        self.meta_api.doc = {
            'definitions': {},
            'paths': {}
            }

        cmdlets_files = self._get_cmdlets_files()
        loaded_cmdlets = self._load_cmdlets_files(cmdlets_files)
        usable_cmdlets = self._get_usable_cmdlets(loaded_cmdlets)

        for line in usable_cmdlets:
            if line['name'] != '':
                cmd_name = line['name'].replace(' ', '/')
                cmd_name = '/' + cmd_name
                parameters_found = line['param'].split(',')
                self.meta_api.doc['paths'][cmd_name] = {
                        'get': {
                            'description': line['cmdlet_description'],
                            'operationId': '',
                            'operation': line['command'],
                            'parameters': [],
                            'responses': {
                                '200': {
                                    'description': line['response_description'],
                                    'schema': {},
                                    'table_order': [],
                                    'multiple_output': line['multiple_output']
                                }
                            },
                            'summary': line['cmdlet_summary'],
                            'tags': '',
                            'x-group': ''
                        }
                    }
                for param in parameters_found:
                    self.meta_api.doc['paths'][cmd_name]['get']['parameters'].append({
                        "in": "body",
                        "name": line['param'],
                        "required": True,
                        "type": "string"
                        })

        self.endpoints = self.meta_api.doc


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
        return filter_list


    #def initialize_callbacker(self, operations, formatter):
    def initialize_callbacker(self, operations):
        #self.formatter = formatter
        self.operations = operations
        #self.cbacker = CallBack(self.operations, self.base_kit, self.formatter)
        self.cbacker = CallBack(self.operations, self.base_kit)


class CmdletsControls():

    def __init__(self, tools):
        self.tools = tools
        self.cmdlets_folder = CONSTANTS.CONF_FOLDER + '/cmdlets'

    def list_cmdlets_profiles(self, kwargs):
        result = []
        profiles = self._get_cmdlets_files()
        for profile in profiles:
            name = profile.replace('.json', '')
            name = name.replace('-cmdlets', '')
            result.append({
                'name': name,
                'path': self.cmdlets_folder + '/' + profile
                })

        return json.dumps(result, indent=2)

    def add_cmdlet_profile(self, kwargs):
        # Get parameters passed to the operation.
        parameters = kwargs['data']
        parameters = json.loads(parameters)

        # Confirm that the cmdlet folder has been created.
        self.tools.safe_create_folder(self.cmdlets_folder)

        # Declare the resulting variables.
        result_str = 'Succeeded'
        new_profile = {'name': ''} 
        new_profile, message = self._compare_provided_expected(parameters,
                                                               new_profile)

        name = new_profile['name']
        path = ''

        # fields are completed.
        if new_profile['name'] == '':
            message.append('Error: Unable to add cmdlet profile without '
                           'essential information.. (name)')
            result_str = 'Failed'
        # Treating name to confirm it has all it needs
        elif '-cmdlets.json' not in name:
            name = name + '-cmdlets'
            path = self.cmdlets_folder + '/' + name + '.json'

        if self.tools.safe_create_json_file([], path) and result_str != 'Failed':
            message.append('Created profile successfully.')
        else:
            result_str = 'Failed'
            message.append('Error: Failed to create profile, please check if '
                          'file with name provided alaredy exists or if is valid...')
        result = {
            'result': result_str,
            'message': message,
            'data': {
                'name': new_profile['name'],
                'path': path
            }
        }

        return json.dumps(result, indent=2)

    def list_cmdlets(self, kwargs):
        cmdlets_files = self._get_cmdlets_files()
        #print(cmdlets_files)
        loaded_cmdlets = self._load_cmdlets_files(cmdlets_files)
        usable_cmdlets = self._get_usable_cmdlets(loaded_cmdlets)

        return json.dumps(usable_cmdlets, indent=2)

    def sync_cmdlets(self, kwargs):
        target_folder = kwargs['target_folder']
        self._update_env_file(target_folder+'/me.json')
        result = {
            'result': 'Applied cmdlets profile to environment configuration.'
        }
        return result

    def _gen_cmdlet(self):
        new_cmdlet = {
                       'id': str(self.tools.gen_uuid()),
                       'profile': 'cmdlets.json',
                       'name': '',
                       'cmdlet_summary': '',
                       'cmdlet_description': '',
                       'command': [],
                       'multiple_output': 'segmented',
                       'param': '',
                       'response_description': ''
                       }
        
        return new_cmdlet

    def _compare_provided_expected(self, provided, expected):

        message = []
        # Get the passed parameters that are expected in the new_cmdlet.
        for key, value in provided.items():
            if key in expected.keys() and key != 'id':
                expected[key] = value
            else:
                message.append('Warning: Ignoring unexpected key: ' + key)

        return expected, message


    def add_cmdlet(self, kwargs):

        # Get target folder from operations.
        target_folder = kwargs['target_folder']

        # Get parameters passed to the operation.
        parameters = kwargs['data']
        try:
            parameters = json.loads(parameters)
        except json.decoder.JSONDecodeError as error:
            msg = str('Json parameter is too complex to be provided with '
                      'simple key assignment, please provide json input...\n')
            raise RbkcliException.ApiHandlerError(msg)


        # Confirm that the cmdlet folder has been created.
        self.tools.safe_create_folder(self.cmdlets_folder)

        # Generate new cmdlet profile
        new_cmdlet = self._gen_cmdlet()

        # Declare the resulting variables.
        result = {'result': 'Succeeded'}
        message = []

        # Get the passed parameters that are expected in the new_cmdlet.
        for key, value in parameters.items():
            if key in new_cmdlet.keys() and key != 'id':
                new_cmdlet[key] = value
            else:
                message.append('Warning: Ignoring unexpected key: ' + key)

        # Validating if provided cmdlet profile exists.
        cmdlets_files = self._get_cmdlets_files()
        #cmdlet_file = ['cmdlets.json']
        prov_prfile = new_cmdlet['profile']
        prov_prfile_file =  prov_prfile + '-cmdlets.json'
        if prov_prfile in cmdlets_files:
            cmdlet_file = [prov_prfile]
            #print(cmdlet_file)
            loaded_cmdlets = self._load_cmdlets_files(cmdlet_file)
        # Validating the name of the profile, without sufix.
        elif prov_prfile_file in cmdlets_files:
            cmdlet_file = [prov_prfile_file]
            #print(cmdlet_file)
            loaded_cmdlets = self._load_cmdlets_files(cmdlet_file)
        # If cmdlets.json file does not exist, then create it automatically.
        elif new_cmdlet['profile'] == 'cmdlets.json':
            loaded_cmdlets = []
            cmdlet_file = str(self.cmdlets_folder + '/' + 'cmdlets.json')
            #print(cmdlet_file)
            self.tools.safe_create_json_file([], cmdlet_file)
        else:
            message.append('Error: Unable to add cmdlet, unrecognized '
                           'profile... (' + new_cmdlet['profile'] + ')')
            result = {'result': 'Failed'}

        # Validating if essential fields are completed.
        if new_cmdlet['name'] == '' or new_cmdlet['command'] == []:
            message.append('Error: Unable to add cmdlet without essential'
                           ' information.. (name, command)')
            result = {'result': 'Failed'}
        else:
            if not isinstance(new_cmdlet['command'], list):
                new_cmdlet['command'] = [new_cmdlet['command']]

        # If status is still succeeded then apply changes.
        if result['result'] == 'Succeeded':
            loaded_cmdlets.append(new_cmdlet)
            #cmdlet_file = ['cmdlets.json']
            self.tools.create_json_file(loaded_cmdlets, 
                                        str(self.cmdlets_folder +
                                        '/' +
                                        cmdlet_file[0]))
            self._update_env_file(target_folder+'/me.json')

        result['message'] = message
        result['cmdlet_to_add'] = new_cmdlet

        return json.dumps(result, indent=2)

    def _update_env_file(self, file):
        file_dict = self.tools.load_json_file(file)
        self._gen_docs()
        file_dict['apis']['cmdlets'] = self.endpoints
        self.tools.create_json_file(file_dict, file)

    def remove_cmdlet(self, kwargs):
        target_folder = kwargs['target_folder']
        result = []
        data = kwargs['data']
        data = json.loads(data)
        cmdlet_id = data['id']
        if not isinstance(cmdlet_id, list):
            cmdlet_id = [cmdlet_id]
        
        for id_ in cmdlet_id:
            result.append(self._remove_cmdlet_id(id_))

        self._update_env_file(target_folder + '/me.json')

        return json.dumps(result, indent=2)

    def _remove_cmdlet_id(self, id_):
        result = {}
        cmdlets_files = self._get_cmdlets_files()
        loaded_cmdlets = self._load_cmdlets_files(cmdlets_files)

        for cmdlet in loaded_cmdlets:
            if id_ == cmdlet['id']:
                result = self._remove_from_file(id_, cmdlets_files)

        if result == {}:
            result = {
                'result': 'Failed.',
                'message': 'No cmdlets found with the provided ID... (' +  id_ + ')'    
            }

        return result

    def _remove_from_file(self, id_, file):
        data = []
        result = {}
        for fil in file:
            profile = self.cmdlets_folder + '/' + fil
            cmdltes_profile = self.tools.load_json_file(profile)
            result_profile = copy.copy(cmdltes_profile)

            for cmd in enumerate(cmdltes_profile):
                if id_ == cmd[1]['id']:
                   result_profile.pop(cmd[0])
                   removed_cmdlet = cmd[1]
                   data.append(removed_cmdlet)
            self.tools.create_json_file(result_profile, profile)
        if data != []:
            result = {
                'result': 'Succeeded.',
                'message': 'Found the following cmdlets with the provided ID(s).',
                'data': data     
            }
        return result

    def patch_cmdlet(self):
        pass

    def _get_cmdlets_files(self):
        cmdlets_files = []
        
        try:
            cmdlets_folder = list(os.listdir(self.cmdlets_folder))
            for file in cmdlets_folder:
                if file.endswith('cmdlets.json'):
                    cmdlets_files.append(file)
        except Exception as e:
            #print(e)
            return []
        return cmdlets_files

    def _load_cmdlets_files(self, cmdlets_files):
        loaded_cmdlets = []

        for file in cmdlets_files:
            profile = self.tools.load_json_file(self.cmdlets_folder + '/' + file)
            profile_final = []
            for cmdleto in profile:
                cmdleto['profile'] = file
                profile_final.append(cmdleto)
            #print(profile_final)
            loaded_cmdlets = loaded_cmdlets + profile_final
        return loaded_cmdlets
    
    def _get_usable_cmdlets(self, loaded_cmdlets):
        usable_cmdlets = []
        usable_cmdlets_list = []
        existing_cmdlets = loaded_cmdlets
        for item in enumerate(existing_cmdlets):
            if item[1]['name'] in usable_cmdlets_list:
                
                item[1]['status'] = 'duplicated'
            else:
                item[1]['status'] = 'usable'
                usable_cmdlets_list.append(item[1]['name'])
            usable_cmdlets.append(item[1])

        return usable_cmdlets

    def _gen_docs(self):
        """Create static API documentation and store to class var."""
        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.
        doc = {
            'definitions': {},
            'paths': {}
            }

        cmdlets_files = self._get_cmdlets_files()
        loaded_cmdlets = self._load_cmdlets_files(cmdlets_files)
        usable_cmdlets = self._get_usable_cmdlets(loaded_cmdlets)

        for line in usable_cmdlets:
            if line['name'] != '':
                cmd_name = line['name'].replace(' ', '/')
                cmd_name = '/' + cmd_name
                parameters_found = line['param'].split(',')
                doc['paths'][cmd_name] = {
                        'get': {
                            'description': line['cmdlet_description'],
                            'operationId': '',
                            'operation': line['command'],
                            'parameters': [],
                            'responses': {
                                '200': {
                                    'description': line['response_description'],
                                    'schema': {},
                                    'table_order': [],
                                    'multiple_output': line['multiple_output']
                                }
                            },
                            'summary': line['cmdlet_summary'],
                            'tags': '',
                            'x-group': ''
                        }
                    }
                for param in parameters_found:
                    doc['paths'][cmd_name]['get']['parameters'].append({
                        "in": "body",
                        "name": line['param'],
                        "required": True,
                        "type": "string"
                        })

        self.endpoints = doc
