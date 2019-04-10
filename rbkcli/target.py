'''API targets module for rbkcli'''

import os
import re

from rbkcli.base import CONSTANTS, DotDict, RbkcliBase, RbkcliException


class RbkcliResponse():
    '''Class to standarize the responses provided by Meta commands.'''

    def __init__(self, status_code=0, text='', raw=''):
        '''.'''
        self.status_code = status_code
        self.text = text
        self.raw = raw

    @classmethod
    def successfull_response(self, func):

        def response_wrapper(self, *args, **kwargs):
            self.text = func(self, *args, **kwargs)
            self.status_code = 200
            return self

        return response_wrapper


class ApiTarget(RbkcliBase):
    '''Define the Target to which we will request APIs from.'''

    def __init__(self, discover_fn, auth={}, env={}, user_profile='admin',
                 base_folder=''):
        '''Initialize Rbkcli Rubrik Cluster.'''

        # Make sure the parent init is run.
        RbkcliBase.__init__(self, user_profile=user_profile, 
                            base_folder=base_folder)

        # req is a dict created from te raw input of API request.
        self.req = {}

        # Load the API target from tools.
        #self.target = self.tools.load_target()
        self.tools = self.tools()
        if auth == {}:
            self.auth = self.tools.load_auth()
        else:
            self.auth = auth
        self.target = self.auth.server

        base_kit = self._gen_base_kit(discover_fn)

        # Load or create environment based on imported apis
        self.environment = EnvironmentHandler(base_kit)

        # Instantiate operations and api handlers
        self.operations = self.environment.evaluate()

        # Instantiate InpuHandler for future use
        self.validator = InputHandler(base_kit, self.operations)

    def execute(self, endpoint, version='', method='get', param='', data={},
                  formatt='raw'):
        '''
        Validate the input provided and call the execute method for the
        provided request.
        '''

        # Generate a dictionary of the data passed for request
        self._gen_req_dict(endpoint, version, method, param, data, formatt)
        
        # Use input handler to validate the data entered.
        # If any error to be raised related to request inconsistency,
        # should come from this
        self.req = self.validator.validate(self.req)

        # Once input is normalize pass it on to request the operation.
        return self.operations.execute(self.req)

    def documentation(self, endpoint, version='', method='get', param='',
                      data={}, formatt='raw'):
        '''.
        Validate the input provided and return the swagger documentation for
        for the provided request.
        '''

        # Generate a dictionary of the data passed for request
        self._gen_req_dict(endpoint, version, method, param, data, formatt)
        
        # Use input handler to validate the data entered.
        # If any error to be raised related to request inconsistency,
        # should come from this
        self.req = self.validator.validate(self.req)

        # Once input is normalize pass it on to request the operation.
        return self.operations.documentation(self.req)

    def information(self, endpoint, version='', method='get', param='',
                      data={}, formatt='raw'):
        '''.
        Validate the input provided and return the swagger documentation for
        for the provided request.
        '''

        # Generate a dictionary of the data passed for request
        self._gen_req_dict(endpoint, version, method, param, data, formatt)
        
        # Use input handler to validate the data entered.
        # If any error to be raised related to request inconsistency,
        # should come from this
        self.req = self.validator.validate(self.req)

        # Once input is normalize pass it on to request the operation.
        return self.operations.information(self.req)


    def _gen_req_dict(self, endpoint, version, method, param, data, formatt):
        '''Generate the request dictionary to be passed.'''

        # Create the dictionary as a dot ddict for easy access.
        req = self.dot_dict()
        req.endpoint = endpoint
        req.version = version
        req.method = method
        req.param = param
        req.data = data
        req.formatt = formatt

        # Save it to instance variable.
        self.req = req

    def _gen_base_kit(self, discover_fn):
        '''Generate a shared context to pass to other classes.'''

        # Create the dictionary as a dot ddict for easy access.
        base_kit = self.dot_dict()
        base_kit.config_dict = self.conf_dict
        base_kit.base_folder = CONSTANTS.BASE_FOLDER
        base_kit.tools = self.tools
        base_kit.logger = self.rbkcli_logger
        base_kit.dot_dict = self.dot_dict
        base_kit.target = self.target
        base_kit.api_handler = self.api_handler
        base_kit.discover_fn = discover_fn
        base_kit.auth = self.auth
        base_kit.user_profile = self.user_profile
        base_kit.json_ops = self.json_ops

        return base_kit


class ApiTargetTools():
    '''Parent Class of handlers for the ApiTarget.'''

    def __init__(self, base_kit):
        '''Initialize ApiTargetTools Class, with shared context.'''
        self.base_kit = base_kit
        self.conf_dict = base_kit.config_dict
        self.rbkcli_logger = base_kit.logger
        self.tools = base_kit.tools
        self.base_folder = base_kit.base_folder
        self.dot_dict = base_kit.dot_dict
        self.target = base_kit.target
        self.api_handler = base_kit.api_handler
        self.discover_fn = base_kit.discover_fn
        self.auth = base_kit.auth
        self.user_profile = base_kit.user_profile
        self.json_ops = base_kit.json_ops


class EnvironmentHandler(ApiTargetTools):
    '''
    Handle all actions related to the environment like load, create,
    node resolution, me.json creation.
    '''
    
    def __init__(self, base_kit):
        '''Initialize EnvironmentHandler class.'''

        ApiTargetTools.__init__(self, base_kit)

        # Result of loading the environment.
        self.env = self.dot_dict()
        self.env.file_name = 'me.json'

        # Dictionary of loading resolution file.
        self.resolution = self.dot_dict()
        self.resolution.file_name = 'target_resolution.json'
        self.resolution.file_path = str(CONSTANTS.CONF_FOLDER + '/' +
                                        self.resolution.file_name)

        # Dictionary that stores what to run to get target ID, environment ID,
        # target version and other targets accepted in this environment.
        self.discovery = self.dot_dict()
        self.discovery.expect_keys = ['id', 'ip', 'envId', 'envName']
        self.discovery.action = self.discover_fn

    def evaluate(self):
        '''
        Verifies if the environment needs to be created or loaded or re-sync.

        For the environment to be considered ready to load it has to have:
        -target_resolution.json
        # File that resolves multiple target IPs to same ApiTarget 
        environment.
        
        -me.json
        # File that contains all available endpoints documented in the 
        swagger.yaml previously acquired.
        
        -cache/
        # Folder that contains cached commands, when requestd.

        After loaded the environment needs to pass the synch check, which
        confirms that the current version is the same as the one the env was
        created

        If evaluation understands environment needs to be created, all
        previous files are created then.
        '''

        # Either will load the self.env.details
        if not self.load():
            if not self.create():
                raise Exception

        # Once the environment is successfully loaded the available -
        # operations are generated.
        self.operations.generate_ops()

        return self.operations

    def load(self):
        '''Load the environmental files.'''

        # Performs resolution verification and best effort fixing.
        if not self._is_resolvable():
            return False
        #print('resolved')

        # _is_resolvable will load the env_id which is the target folder name.
        if not self._is_loadable():
            return False
        #print('loaded')
        #if not self._is_current():
        #    return False

        # Will get the APIs from the file and instantiate a Operation.
        if not self._is_exportable():
            return False
        #print('exported')
        return True

    def _is_resolvable(self):
        '''Check if resolution file exists and returns valid results.'''

        # Attempts to load the resolution file.
        try:
            self.resolution.data = self.tools.load_json_file(
                self.resolution.file_path)
        except RbkcliException.ToolsError as error:

            # If fails log and error, attempts to recreate file.
            msg = str('TargetError # Failed to load [%s] file, attempting'
                      ' to recreate the [%s] file. %s' %
                      (self.resolution.file_name,
                       self.resolution.file_name,
                       error))
            self.rbkcli_logger.error(msg)
            self._recreate_resolution_file()

            # After recreation tries to load again.
            try:
                self.resolution.data = self.tools.load_json_file(
                    self.resolution.file_path)

            # If it fails, return false.
            except RbkcliException.ToolsError as error:
                return False

        # Finally try to resolve target, returns True or False.
        return self._is_resolved()

    def _is_resolved(self):
        '''
        With the resolution data received attemps to resolve target into a
        known environment ID.
        '''

        # If target is resolved, env_id will be loaded with a UUID.
        self.env.id = ''

        # Go through resoltuion data and match the target with registry.
        if self.resolution.data != '' and self.resolution.data != []:
            for node in self.resolution.data:
                if node['ip'] == self.target:
                    # First resolution found is returned.
                    self.env.id = node['envId']
                   
                    # Logs successfull target-environment resolution.
                    msg = str('Target # Successfully resolved target [' + 
                              self.target + '] into environment ID [' +
                              self.env.id + ']' )
                    self.rbkcli_logger.debug(msg)

                    # Return success.
                    return True

        # Logs unsuccessfull target-environment resolution.
        msg = str('TargetError # Failed to resolve the target IP into a'
                  'environment ID, will attempt to download/load API docs and'
                  ' recreate environment file.')
        self.rbkcli_logger.error(msg)

        # If no target was matched returns False.
        return False

    def _is_loadable(self, file_path=''):
        '''Check if me file exists and returns valid results.'''

        # Allow reuse of the function by allowing to pass existing file.
        if file_path != '':
            self.env.file_path = file_path
        else:
            # Build the paths to the environment file to load.
            self.env.folder = CONSTANTS.TARGETS_FOLDER + '/' + self.env.id
            self.env.file_path =  self.env.folder + '/' + self.env.file_name

        # Attempt to loas the environment file.
        try:
            file_dict = self.tools.load_json_file(self.env.file_path)
            for key, value in file_dict.items():
                self.env[key] = value
        
        # If it fails logs an error and returs False.
        except RbkcliException.ToolsError:
            msg = str('TargetError # Failed to load [%s] environment file'
                      ', will attempt to download API docs and create a new '
                      '[%s].' % (self.env.file_name, self.env.file_name))
            self.rbkcli_logger.error(msg)
            return False

        # Assuming it succeeds, logs successfull loading action.
        msg = str('Target # Successfully loaded environment file: [' +
                  self.env.file_name + ']')
        self.rbkcli_logger.debug(msg)

        # Assuming it succeeds, return if what is loaded is valid.
        return self._is_valid()

    def _is_valid(self):
        '''Verify bare minimun requirements for a env file.'''

        # Checks if env file contains the needed keys.
        msg = str('Target # Successfully verified keys in environment file:'
                  ' [' + self.env.file_name + ']')
        self.rbkcli_logger.debug(msg)

        return True

    def _is_current(self):
        '''Discover target and confirm if loaded version is current.'''

        ### Check this out.
        if not self._is_discoverable():
            raise Exception('Connection error')

        # Verify discovered data versus loaded data.

        ##### THIS CANNOT BE PERFORMED AT EVERY COMMAND.
        return True

    def _is_exportable(self):
        '''Export the loaded Api data to Operations Handler.'''

        ### Check this out.
        #try:
        self.operations = OperationsHandler(self.base_kit,
                                            self.env.imported_api_v)
        self.operations.export_apis(self.env.apis)
        
        # Provide APIs to metacommands for.
        self.operations.handler.rbkcli.all_apis = self.env.apis
        return True
        #except Exception:
        #    return False

    def create(self):
        '''Create environmental file by getting uniq identifier.'''

        # Based in the pre-loaded discovery dictionary:
        # Instantiate the discovery handlers.
        # Execute the discovery APIs
        if not self._is_discoverable():
            return False
        #print('discoverable')

        # Assumin its discovered will instantiate ApiHandlers and import APIs.
        if not self._is_importable():
            return False
        #print('importable')

        # Assuming the imports worked fine, we create env folder
        if not self.tools.safe_create_folder(self.env.folder):
            msg = 'Unable to create new target folder.'
            raise RbkcliException.ClusterError(msg)

        # Assuming the imports worked fine, we create the env file
        self.tools.create_json_file(self.env, self.env.file_path)

        # Assuming the creation of the environment completed successfully we
        # update/create the target resolution file.
        self._update_resolution_file()

        return True

    def _is_discoverable(self):
        '''Verify if target is discoverable.'''

        # Runs the provided discovery action upon instantiation.
        self.discovery.results = self.discovery.action()
        self.env.discovery = self.discovery.results
        #print(self.discovery.results)

        # Verify if the result is correct type and has necessary data.
        if not self._is_discovery_valid():
            return False

        # Assuming it does, loads that to the environment.
        self.env.id = self.discovery.results[0]['envId']

        # Build the paths to the environment file to create.
        self.env.folder = CONSTANTS.TARGETS_FOLDER + '/' + self.env.id
        self.env.file_path =  self.env.folder + '/' + self.env.file_name

        # Assuming discovery went fine, we log and return
        msg = str('Target # All expected discovery keys are valid.')
        self.rbkcli_logger.debug(msg)
        return True

    def _is_discovery_valid(self):
        '''Verify each key return for validity.'''

        # Expects to receive a dictionary with 4 keys.
        if not isinstance(self.discovery.results, list):
            print('Results not List')
            ## FIX THIS
            return False

        # Validate if the expected discovery keys are here.
        for key in self.discovery.expect_keys:
            # Load the error msg in case it happens
            msg = str('TargetError # Expected discovery key is invalid '
                      '[%s].' % key)
            try:
                for target_resolution in self.discovery.results:
                    value = target_resolution[key]

                    # If they are empty raise a exception.
                    if value == '' or value == []:
                        self.rbkcli_logger.error(msg)
                        raise Exception

                return True
            # If the key is not present log error and raise exception
            except KeyError:
                self.rbkcli_logger.error(msg)
                raise Exception
    
    def _is_importable(self):
        '''Instantiate Operations and import Apis.'''
         
         ### Check this out.
        try:
            self.operations = OperationsHandler(self.base_kit,
                               CONSTANTS.SUPPORTED_API_VERSIONS)
            self.env.apis = self.operations.import_apis()
            self.env.imported_api_v = self.operations.instantiated_api_versions
            
            # Provide APIs to metacommands for listing commands.
            self.operations.handler.rbkcli.all_apis = self.env.apis

            return True
        except Exception:
            print('Unable to imort ')


    def _update_resolution_file(self):
        '''Update target_resolution file with newly discovered nodes.'''

        # Run is resolvable to load/recreate existing resolution data.
        # Attempts to load the resolution file.
        try:
            self.resolution.data = self.tools.load_json_file(
                self.resolution.file_path)
        except RbkcliException.ToolsError:
            self.resolution.data = []

        # Loop through targets returned during discovery.
        for target in self.env.discovery:
            target_resolution = self.dot_dict()
            target_resolution.id = target['id']
            target_resolution.ip = target['ip']
            target_resolution.envId = target['envId']
            target_resolution.envName = target['envName']
            self.resolution.data.append(target_resolution)

        # Remove any duplicated entry:
        data = self.resolution.data
        self.resolution.data = [
            i for n,
            i in enumerate(data) if i not in data[n + 1:]
            ]

        # Recreate resolution file with the validated uniq values
        self.tools.create_json_file(self.resolution.data, 
                                    self.resolution.file_path)

    def _recreate_resolution_file(self):
        '''Load all available environments and recreates the resolution file.'''
        
        # If recreation was asked, resolution data will be reloaded.
        self.resolution.data = []

        # Verify if target folders exists.
        if (os.path.isdir(CONSTANTS.TARGETS_FOLDER)):

            # For each discovered folder, attempt to load env file.
            for directories in os.listdir(CONSTANTS.TARGETS_FOLDER):
                target_dir = CONSTANTS.TARGETS_FOLDER + '/' + directories
                me_file = target_dir + '/' + self.env.file_name

                # If the folder found is a folder, if file exists and name of
                # the env folder is a UUID, then load it.
                if (os.path.isdir(target_dir) and
                        self.tools.is_valid_uuid(directories) and
                        os.path.isfile(me_file)):
                    try:
                        # Will try to load and update the resolution file.
                        self._is_loadable(me_file)
                        self._update_resolution_file()
                    except Exception:
                        raise Exception


class OperationsHandler(ApiTargetTools):
    '''Handle all the API and endpoint listing, instantiates ApiHandlers.'''
    
    class Decorators():
        '''Decorators that share the OperationsHandlers variables.'''

        @classmethod
        def version_looper(self, func):
            '''Loop apis versions available/supported.'''
            
            def inner_loop(self, *args):
                '''Loop version and return dictionary with results.'''
                
                # Dictionary defined as a dot_dict for easy management.
                result = {}
                for value in self.apis_to_instantiate:
                    result[value] = func(self, value, *args)
                return result

            return inner_loop

    def __init__(self, base_kit, apis_to_instantiate):
        '''Initialize Operations Handler class.'''
        ApiTargetTools.__init__(self, base_kit)

        # Declare the dict that will hold the ApiHandlers.
        self.handler = self.dot_dict()

        # Assign the pertinent config changes (white/black lists).
        self.ops_list_changers = self.dot_dict({
                'whitelist': self.conf_dict['config']['whiteList']['value'],
                'blacklist': self.conf_dict['config']['blackList']['value']
            })

        # Declare the lists that will hold all ops and filtered ops.
        self.ops = []
        self.raw_ops = []

        # Assign the Api versions (list) to be instantiated with handlers.
        self.apis_to_instantiate = apis_to_instantiate
        self.instantiated_api_versions = []

        # Perform the instantiation.
        self._instantiate_api_handlers()

        # Perform rbkcli meta instantiation.
        self._instantiate_rbkcli_handler()


    def _instantiate_rbkcli_handler(self):
        '''Instantiate the rbckcli handler to act as a imported API.'''

        version = 'rbkcli'
        self.handler[version] = RbkcliMetaCmds(self.user_profile,
                                               self.base_kit)

    @Decorators.version_looper
    def _instantiate_api_handlers(self, version):
        '''Instantiate Api Handlers from base module.'''

        # Loop through list of predefined apis to instantiate the versions.
        self.handler[version] = self.api_handler(self.auth, version)

    @Decorators.version_looper
    def export_apis(self, version, loaded_apis):
        '''Provided the apis previously loaded export to handlers.'''

        # Get loaded API as external dict argument and load to handler.
        self.handler[version].endpoints = loaded_apis[version]

        # Generate endpoints list for command execution.
        self.handler[version].gen_authorization_lists()
        
        # Create list of successfully instantiated API.
        self.instantiated_api_versions.append(version)

    @Decorators.version_looper
    def import_apis(self, version):
        '''Import the Apis that were instantiated.'''

        # Import API based in the predefined versions.
        api_result = self.handler[version].import_api()
        if api_result != {}:

            # Generate endpoints list for command execution.
            self.handler[version].gen_authorization_lists()

            # Create list of successfully instantiated API.
            self.instantiated_api_versions.append(version)
        else:
            # Remove unecessary handlers
            del self.handler[version]

        return api_result

    def generate_ops(self):
        '''Generate list of all available operations for target.'''

        # Loop through versions and create full list and a list based in the
        # user profile.
        
        #for version in self.apis_to_instantiate:
        for version in self.instantiated_api_versions:
            self.raw_ops = list(self.raw_ops +
                                 self.handler[version].filter_lists['dev'])
            self.ops = self.ops + self.handler[version].focus_list

        # Apply white/black list defined in the configuration file.
        self._apply_whitelist()
        # Black List takes priority, whatever is defined there won't show.
        self._apply_blacklist()
        self.ops.sort()

        if self.ops == [] and self.raw_ops == []:
            raise Exception('Empty Operations list')

        # Passing all available cmds to meta cmds handler.
        self.handler['rbkcli']._store_all_ops(self.ops)

        # Log Successfull action.
        msg = str('Target # Successfully generated list of authorized '
                  'endpoints for user profile: [' + self.user_profile + ']')
        self.rbkcli_logger.debug(msg)
        
    def _apply_whitelist(self):
        '''Apply changes from whitelist in config file to ops list.'''
        if self.ops_list_changers.whitelist != []:

            # For each line in the list, it will verify if that line exists,
            # in the complete list received from APIs.
            for changes in self.ops_list_changers.whitelist:
                for operation in self.raw_ops:

                    # If the change request exists it is then added to the
                    # filtered list.
                    if changes == operation:

                        # The changes are applied to both handlers list.
                        version = changes.strip().split(':')
                        self.handler[version[0]].focus_list.append(operation)
                        self.ops.append(operation)

    def _apply_blacklist(self):
        '''Apply changes from blacklist in config file to ops list.'''
        if self.ops_list_changers.blacklist != []:

            # For each line in the list, it will verify if that line exists,
            # in the complete list received from APIs.
            for changes in self.ops_list_changers.blacklist:
                for operation in self.raw_ops:

                    # If the change request exists it is then removed from
                    # filtered list.
                    if changes == operation:

                        # The changes are applied to both handlers list.
                        version = changes.strip().split(':')
                        self.handler[version[0]].focus_list.remove(operation)
                        self.ops.remove(operation)

    def execute(self, req):
        '''Request execution of operation to ApiHandler.'''
        
        # Attribute request dictionary.
        self.req = req

        # Simplify variables to pass to handler.
        final_endpoint = str(self.req.endpoint + self.req.inline_query +
                             self.req.param)
        version = self.req.version

        # Call handler execute_api method for the request provided.
        api_result = self.handler[version].execute_api(self.req.method,
                          final_endpoint,
                          endpoint_key=self.req.endpoint_key[0],
                          params=self.req.param,
                          data=self.req.data)

        # Return the result of API request.
        return api_result

    @RbkcliResponse.successfull_response
    def documentation(self, req):
        '''Request execution of documentation to ApiHandler.'''

        # Attribute request dictionary.
        self.req = req

        # Retrieving the documentation information from API handler.
        endpoint_paths = self.handler[self.req.version].endpoints['paths']
        doc_result = endpoint_paths[self.req.endpoint_matched][self.req.method]

        # Instantiating json_ops object.
        my_json = self.json_ops(doc_result)
        definitions = self.handler[self.req.version].endpoints['definitions']

        # Using json ops to resolve references in the documentation.
        doc_result = my_json.resolve_ref(definitions)

        # Generating a result dictionary
        api = '/%s%s -%s' % (self.req.version, self.req.endpoint_matched,
                             self.req.method)
        result = {
            'request': api,
            'doc': doc_result
        }

        return self.tools.json_dump(result)

    @RbkcliResponse.successfull_response
    def information(self, req):
        '''Request information from ApiHandler.'''

        # Attribute request dictionary.
        self.req = req

        # Retrieving the documentation information from API handler.
        endpoint_paths = self.handler[self.req.version].endpoints['paths']
        doc_result = endpoint_paths[self.req.endpoint_matched][self.req.method]

        # Instantiating json_ops object.
        my_json = self.json_ops(doc_result)
        definitions = self.handler[self.req.version].endpoints['definitions']

        # Using json ops to resolve references in the documentation.
        doc_result = my_json.resolve_ref(definitions)

        # Generating a result dictionary

        return self._gen_info_output(doc_result)

    def _gen_info_output(self, doc_result):
    
        description = '%12s [%s]' % ('Description:', doc_result['description'])
        endpoint = '%12s [/%s%s]' % ('Endpoint:', self.req.version, self.req.endpoint_matched)
        method = '%12s [%s]' % ('Method:', self.req.method)
        parameters = '%12s [%s]' % ('Parameters:', str(len(doc_result['parameters'])))
        output = [description, endpoint, method, parameters]
        
        for params in doc_result['parameters']:
            param_name = '%12s -%s' % (' ', params['name'])
            output.append(param_name)
            param_desc = '%14s %s %s.' % (' ', 'Description:', params['description'])
            output.append(param_desc)
            if not params['required']:
                require = 'NOT '
            else:
                require = ''
            add_info = str('%14s %s This parameter is %sREQUIRED to run and '
                           'should be provided in the %s as a %s.\n' %
                           (' ', 'Additional info:', require, params['in'],
                            params['type']))
            output.append(add_info)

        return '\n'.join(output)

class InputHandler(ApiTargetTools):
    '''
    Handle all the API and endpoint listing, connects with the ApiHandler.

    Available fields to be passed to cluster.order() are:
        self.req = req
        self.req.endpoint = ''
        self.req.version = ''
        self.req.method = ''
        self.req.parameter = {}
        self.req.data = {}
        self.req.formatt = ''
    This class will make sure each of those fields are valid.
    '''

    def __init__(self, base_kit, operations):
        '''Initialize InputHandler class.'''
        ApiTargetTools.__init__(self, base_kit)

        self.req = self.dot_dict()
        self.operations = operations
        self.error = ''

    def validate(self, req):
        '''Validate the request format and consistency to be able to exec.'''

        # Atributing to its own req instance as dot dict.
        self._assing_request(req)

        # Transfor endpoint to list and remove possible provided version.
        self._normalize_endpoint()
        self._extract_version_inline()

        if not self._is_valid_endpoint():
            error = 'The provided endpoint is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error + ' ' + self.error)

        if not self._is_valid_version():
            error = 'The provided version is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)            

        if not self._is_valid_method():
            error = 'The provided method is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)            

        if not self._is_valid_data():
            error = 'The provided data is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)            

        if not self._is_valid_query():
            error = 'The provided query is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)            

        if self.req.formatt not in CONSTANTS.SUPPORTED_OUTPUT_FORMATS:
            error = 'The requested formatt is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)            

        if self.req.endpoint_key == []:
            error = str('Could not find any available command with'
                        ' the provided combination of method and endpoint.')
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)            


        # Assuming validation was completed successfully, logging n returning.
        msg = str('Rbkcli # Validation succeeded for provided arguments [%s]'
                  % self.req_ops.simple_dict_natural()) 
        self.rbkcli_logger.debug(msg)      
        return self.req

    def _is_valid_endpoint(self):
        '''Confirm if provided endpoint is valid.'''

        if not self._split_endpoint_arguments():
            return False
        if not self._gen_endpoint_key():
            return False

        # If normalization fails, fail the validation.
        if not isinstance(self.req.endpoint, str):
            return False

        return True

    def _split_endpoint_arguments(self):
        '''Split and parse provided endpoint.'''
        
        self.req.not_verified = []

        self.req.endpoint_parsed = self.req.endpoint.copy()
        while not self._match_endpoint() and len(self.req.endpoint_parsed) > 0:
            self.req.not_verified.append(self.req.endpoint_parsed[-1])
            self.req.endpoint_parsed.pop(-1)

        self.req.not_verified.reverse()
        self.req.endpoint = '/'.join(self.req.endpoint_parsed)
        self.req.endpoint_matched = '/' + '/'.join(self.req.endpoint_matched)
        self.req.endpoint_search = str(self.req.version + ':' +
                                       self.req.endpoint_matched +
                                       ':' + self.req.method)

        if self.req.not_verified != []:
            error = str('There are arguments that could not be parsed [%s].' %
                        " ".join(self.req.not_verified))
            msg = 'RbkcliError # ' + error
            self.error = error
            self.rbkcli_logger.error(msg)
            return False

        return True

    def _gen_endpoint_key(self):
        '''Generate endpoint key for request.'''
        # Using the matched endpoint get the endpoint key.
        self.req.endpoint_key = []
        for line in self.operations.ops:
            if self.req.endpoint_search in line:
                self.req.endpoint_key.append(line)

        # If endpoint key is empty logg error and return false.
        if self.req.endpoint_key == []:
            error = str('Unable to find any endpoint and method combination '
                        'that matches the provided [%s].' %
                        (self.req.endpoint_search))
            msg = 'RbkcliError # ' + error
            self.error = error
            self.rbkcli_logger.error(msg)
            return False

        return True

    def _match_endpoint(self):
        '''Parse and match endpoint with the available list.'''

        self.req.endpoint_matched = ''
        for auth_edpt in self.operations.ops:
            auth_v, auth_end, auth_meth, auth_mt = auth_edpt.strip().split(':')
            auth_end = auth_end.strip().split('/')
            auth_end = list(filter(None, auth_end))

            for block in enumerate(auth_end):
                if block[0] <= len(self.req.endpoint_parsed)-1:

                    if (block[1] == self.req.endpoint_parsed[block[0]] or
                       re.search('\{*id\}', block[1])):

                        if (block[0] == len(self.req.endpoint_parsed)-1 and
                           len(auth_end) == len(self.req.endpoint_parsed)):

                            self.req.endpoint_matched = auth_end
                            return True
                    else:
                        break
        return False

    def _normalize_endpoint(self):
        '''Convert endpoint to list, without API version inline.'''

        # Convert from list to string.
        if isinstance(self.req.endpoint, list):
            self.req.endpoint = " ".join(self.req.endpoint)

        # Remove inline parameters:
        if '?' in self.req.endpoint and ' ' in self.req.endpoint:
            raise Exception
        elif '?' in self.req.endpoint:
            self.req.endpoint = self.req.endpoint.strip().split('?')
            self.req.inline_query = '?' + self.req.endpoint[1]
            self.req.endpoint = self.req.endpoint[0]
        else:
            self.req.inline_query = ''

        # If its string, treat cases of space/slash separated arguments.
        if isinstance(self.req.endpoint, str):
            if ' ' in self.req.endpoint and '/' in self.req.endpoint:
                raise Exception
            elif ' ' in self.req.endpoint:
                self.req.endpoint = self.req.endpoint.strip().split(' ')
            elif '/' in self.req.endpoint:
                self.req.endpoint = self.req.endpoint.strip().split('/')
            else:
                self.req.endpoint = [self.req.endpoint]

        # Remove empty elements from list.
        self.req.endpoint = list(filter(None, self.req.endpoint))

    def _extract_version_inline(self):
        '''Parse and attribute version from endpoint.'''

        # Verify if version was provided with endpoint
        if self.req.endpoint[0] in CONSTANTS.SUPPORTED_API_VERSIONS:
            
            # If it was, store that version in another var and remove from-
            # endpoint variable
            self.req.inline_version = self.req.endpoint[0]
            self.req.endpoint.pop(0)
        
        # If not in endpoint then inline is consider same as provided version.
        else:
            self.req.inline_version = self.req.version

    def _is_valid_version(self):
        '''Confirm if provided version is valid.'''

        # Get the version from the endpoint matched.
        self.req.key_version = self.req.endpoint_key[0].strip().split(':')
        self.req.key_version = self.req.key_version[0]

        # If both inline and provided versions are blank, use the found one.
        if self.req.version == '' and self.req.inline_version == '':
            self.req.version = self.req.key_version

        # If only the provided version is empty, confirm if the remaining-
        # ones match.
        elif self.req.version == '':
            if self.req.key_version != self.req.inline_version:
                return False
            else:
                self.req.version = self.req.key_version

        # If only the inline version is empty, confirm if the remaining-
        # ones match.
        elif self.req.inline_version == '':
            if self.req.key_version != self.req.version:
                return False

        # If final received validation is not in the instanciated versions,
        # it fails the test.
        if self.req.version not in self.operations.apis_to_instantiate:
            return False

        # Assuming all ifs passes, validation is succeeded.
        return True

    def _is_valid_method(self):
        '''Confirm if provided method is valid.'''
        if (self.req.method not in
           CONSTANTS.SUPPORTED_USER_METHODS[self.user_profile]):
            return False
        return True

    def _is_valid_data(self):
        '''Confirm if provided data is valid.'''
        if '{' not in self.req.data and type(self.req.data) != dict:
            data_ops = self.json_ops()
            self.req.data = data_ops.natural_simple_dictstr(self.req.data)  

        return True

    def _is_valid_query(self):
        '''Confirm if provided query is valid.'''

        # For query entered with comma separated arguments replace with &.
        self.req.param = self.req.param.replace(',', '&')
        
        # If both ainline query and CLI query are entered concatenate them.
        if self.req.inline_query == '':
            if self.req.param != '':
                self.req.param = '?' + self.req.param
        elif self.req.param != '':
            self.req.param = '&' + self.req.param
        
        return True

    def _assing_request(self, req):
        '''Create instance request as dot dict.'''
        self.req_ops = self.json_ops(req)

        for key in req.keys():
            self.req[key] = req[key]


class RbkcliMetaCmds(ApiTargetTools):
    '''
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

    '''

    def __init__(self, user_profile, base_kit):
        '''Initialize Meta commands class.'''

        ApiTargetTools.__init__(self, base_kit)

        self.user_profile = user_profile
        self.version = 'rbkcli'
        self.filter_lists = {}
        self._gen_docs()
        self._gen_exec_dict()
        self._gen_exec_api()


    def gen_authorization_lists(self):
        '''
        Create custom lists of authorized based in the user profile
        that was instantiated.
        The focus list is used to verify if the API can be executed or not.
        '''
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
        '''Return the generated API doc for the meta commands.'''
        return self.api_doc

    def execute_api(self, method, endpoint, params='', data={}, 
                    endpoint_key=''):
        '''Execute method based in the endpoint and method entered.'''
        if '?' in endpoint:
            endpoint, query = endpoint.split('?')
        else:
            query = ''

        return self.exec_api['paths']['/'+endpoint][method]['exec_fn'](query)

    def _gen_exec_dict(self):
        '''Generate translation between endpoints and public methods.'''
        self.exec_dict = {
            'commands_get': self.ops_commands_get,
            'commands_search_get': self.ops_commands_search_get
            }

    def _gen_exec_api(self):
        '''Apply public method to dictionary with endpoint documentation.'''
        # FIX this.
        self.exec_api = self.tools.cp_dict(self.api_doc)
        for method, method_fn in self.exec_dict.items():
            path = method.strip().split('_')
            api_method = path[-1]
            path.pop(-1)
            path = '/' + '/'.join(path)
            try:
                self.exec_api['paths'][path][api_method]['exec_fn'] = method_fn
            except KeyError:
                pass

    def _gen_docs(self):
        '''Create static API documentation and store to class var.'''

        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.
        self.api_doc = {
            'definitions': {},
            'paths':{
                '/commands': {
                    'get':{
                        'description': str('Retrieve a list of all the '
                                           'available commands on rbkcli, '
                                           'including all APIs imported.'),
                        'operationId': 'queryAvailableCommands',
                        'parameters': [''],
                        'responses': {
                            '200': {
                                'description': str('Returns a list of avail'
                                                   'able commands'),
                                'schema': {} 
                            }
                        },
                        'summary': 'List available commands',
                        'tags': [
                            '/commands'
                        ],
                        'x-group': 'commands'
                    }
                },
                '/commands/documentation':{
                    'get':{
                        'description': '',
                        'operationId': '',
                        'parameters': '',
                        'responses': '',
                        'summary': '',
                        'tags': '',
                        'x-group': ''
                    }                    
                }
            }
        }

    def _create_all_methods_list(self, field='summary', string='TOKEN'):
        '''Create a list of all defined methods for meta commands.'''

        filter_list = []
        string_ = string.replace(' ', '_')

        for endpoint, endpoint_data in self.api_doc['paths'].items():
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

    @RbkcliResponse.successfull_response
    def ops_commands_get(self, params):
        '''
        Retrieve a list of all the available commands on rbkcli, including
        all APIs imported.
        '''
        result_op = []
        result_dict = []
        commands_table = ['']

        if params != '':
            params = params.split(' ')
            params = '/'.join(params)
            for op in self.all_ops:
                if params in op:
                    result_dict.append(self._generate_op_json(op))
        else:
            for op in self.all_ops:
                result_dict.append(self._generate_op_json(op))

        if len(result_dict) > 0:
            summary = 'Number of commands found'
            commands_ops = self.json_ops()
            commands_table = commands_ops.simple_dict_table(result_dict,
                                                        summary=summary)

        #ops_response = MetaResponse(200, text='\n'.join(commands_table))

        return '\n'.join(commands_table)

    def _generate_op_json(self, op):
        '''Generates the json of the available commands for the target.'''
        op_dict = []
        version, endpoint, method, comment = op.split(':')
        endpoint_cmd = endpoint.split('/')
        endpoint_cmd = ' '.join(endpoint_cmd[1:])
        op_dict = {
            'version': version,
            'endpoint': endpoint_cmd,
            'method': method,
            'summary': str(
                self.all_apis[version]['paths'][endpoint][method]['summary'])
            }

        return op_dict

    def _store_all_ops(self, ops):
        '''Stores all operations in intance variable, stetic reason.'''
        self.all_ops = ops

    def ops_commands_search_get(self, param):
        '''
        Retrieve a list of filtered available commands on rbkcli, including
        all APIs imported. Filter provided with param.
        '''

        print(param)


class RubrikCluster(ApiTarget):
    '''
    Class to instanciate a API target, which is specifically a Rubrik Cluster,
    has a dicovery_action for the target that could be different per target
     type.
    '''

    def __init__(self, auth={}, env={}, user_profile='admin', base_folder=''):
        '''Initialize Rbkcli Rubrik Cluster.'''

        discover_fn = self._discovery_action
        ApiTarget.__init__(self, discover_fn=discover_fn,
                           auth=auth,
                           env=env,
                           user_profile=user_profile,
                           base_folder=base_folder)

    def _discovery_action(self):
        '''Gather cluster and nodes data, returns list of dict.'''
        
        # Declare the target resolution var that will be returned.
        resolution_data = []
        target_resolution = self.dot_dict()

        # Instantiate the raw Api Requester.
        requester = self.api_requester(self.auth)

        # Request the data from the target.
        cluster_data = requester.demand('get', '/v1/cluster/me')
        node_data = requester.demand('get', '/internal/node')

        # Convert data to usable dict.
        node_dict = self.tools.json_load(node_data.text)
        cluster_dict = self.tools.json_load(cluster_data.text)
        node_dict = node_dict['data']

        # Assign value from received data to final dict to be returned.
        for node in node_dict:
            target_resolution.envId =  cluster_dict['id']
            target_resolution.envName =  cluster_dict['name']
            target_resolution.id = node['id']
            target_resolution.ip = node['ipAddress']
            resolution_data.append(target_resolution)
            target_resolution = self.dot_dict()

        return resolution_data


class RbkcliTarget():
    '''
    Class to manage Target Groups.

    Based on provided configuration, will instantiate multiple RubrikClusters.
    Verify if their version is compatible and provide the same operations as
    any other ApiTarget for Cli to be dynamically created.
    This should be a management layer, to deal with multiple targets and
    sessions still keeping consistency of the one CLI.
    Also will normalize multiple API responses into one output, provide access
    to individual targets and targetGroup

    Predicted to be implemented in version 1.3
    rbk_cli = RbkCliTarget(auth=auth)
    rbk_cli.add_target(auth=auth1)
    rbk_cli.add_target(auth=auth2)
    rbk_cli.target_group.list()
    rbk_cli.target_group.execute()
    rbk_cli.target.<server_IP>.execute()
    
    '''

    def __init__(self, auth={}, env={}, user_profile='admin', base_folder=''):
        '''Initialize RbkcliTarget class.'''

        # Attribute the to instance var the instantiation of a Cluster.
        self.target = RubrikCluster(auth=auth,
                                    env=env,
                                    user_profile=user_profile,
                                    base_folder=base_folder)
        
        #self.operations =  self.cli_target.operations
        #self.execute = self.cli_target.execute
        #self.documentation = self.cli_target.documentation

    def add_target(self):
        '''Future method to dynamically add targets to the rbkcli execution.'''
        pass

## Fix all Exceptions, review and improve them.
## Show summary of the endpoint in the rbkcli commands
## Provide autocomplete for query
## Cleanup and ask for testing.
