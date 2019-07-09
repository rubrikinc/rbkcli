"""Meta commands module for rbkcli."""

import os
import json
import copy
import sys
import pkgutil
import importlib
import inspect
from rbkcli.base import CONSTANTS, RbkcliException
from rbkcli.base.essentials import DotDict
from rbkcli.core.handlers import ApiTargetTools, RbkcliResponse
from rbkcli.core.handlers.callback import CallBack


class AnyApiHandler(ApiTargetTools):

    def __init__(self, user_profile, base_kit, version):

        ApiTargetTools.__init__(self, base_kit)
        self.user_profile = user_profile
        self.base_kit = base_kit
        self.version = version
        self.filter_lists = {}

        self.focus_list = []
        self.all_ops = []
        self.all_apis = {}

        self.meta_api = self.dot_dict()
        # Define the path to search.
        self.scripts_folder = CONSTANTS.BASE_FOLDER + '/scripts'


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
        return self._execute_api(args, kwargs)

    def _gen_docs(self):
        """Create static API documentation and store to class var."""
        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.
        self.meta_api.doc = ''
        return


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

    def initialize_callbacker(self, operations):
        #self.formatter = formatter
        self.operations = operations
        #self.cbacker = CallBack(self.operations, self.base_kit, self.formatter)
        self.cbacker = CallBack(self.operations, self.base_kit)


class Customizer(AnyApiHandler):

    def __init__(self, user_profile, base_kit):

        AnyApiHandler.__init__(self, user_profile, base_kit, 'scripts')

    def _gen_docs(self):
        """Create static API documentation and store to class var."""

        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.

        self.meta_api.doc = {
            'definitions': {},
            'paths': {}
            }

        #search_path = '/tmp'
    
        # Define classes that are instantiable:
        intantiable_class = '(<class \'rbkcli.core.handlers.customizer.RbkCliBlackOps'
        # Get liat of folders in the path.
        scripts_paths = [x[0] for x in os.walk(self.scripts_folder)]
        # Iterate each folder.
        for path in scripts_paths:
            # Get a list of modules inside the folder.
            module_path = [x[1] for x in pkgutil.iter_modules(path=[path])]
            # Iterate each module.
            for script in module_path:
                # Make path tangible
                sys.path.append(path)
                # Import module in the path.
                script_module = importlib.import_module(script)
                # Get objects from the module. 
                script_members = inspect.getmembers(script_module)
                # Iterate members of module.
                for member in script_members:
                    member_desc = str(member[1])
                    # Verify members that are a class.
                    if member_desc.startswith('<class '):
                        # Copy the class into a object.
                        myoperation = getattr(script_module, member[0])
                        class_base = str(myoperation.__bases__)
                        # If the parent of th e class is a instantiable class
                        if class_base.startswith(intantiable_class):
                            # Create dictionary from script members
                            script_dict = {}
                            # Attribute values to dict
                            for line in script_members:
                                key, value = line
                                script_dict[key] = value
                            
                            # Instantiate a object of the class.
                            instance = myoperation('')

                            # Attribute values to the instance for doc gen.
                            instance.module = script_dict['__name__']
                            instance.file = script_dict['__file__']
                            instance.class_name = member[0]

                            # Generate documentation
                            self._gen_doc_script(instance)
        
        # Attribute all documentation generated to endpoints.
        self.endpoints = self.meta_api.doc
    
    def _gen_doc_script(self, instance):
        self.meta_api.doc['paths'][instance.endpoint] = {
        instance.method: {
            'description': instance.description,
            'operationId': instance.class_name,
            'source': instance.file,
            'operation': instance.module,
            'parameters': instance.parameters,
            'responses': {
                '200': {
                    'description': '',
                    'schema': {},
                    'table_order': [],
                    'multiple_output': ''
                }
            },
            'summary': instance.summary,
            'tags': '',
            'x-group': ''
            }
        }

    def _execute_api(self, *args):

        # split arguments as needed
        args, kwargs = args
        method, endpoint = args

        # identify what might be a query to the API.
        if '?' in endpoint:
            endpoint, query = endpoint.split('?')
        else:
            query = ''

        # Get endpoint doc
        api = self.meta_api.doc['paths']['/' + endpoint][method]

        # Treat source to be a importable path.
        source = api['source'].split('/')
        source = source[:-1]
        source = '/'.join(source)

        # Import it.
        sys.path.append(source)
        mio_commando = importlib.import_module(api['operation'])

        # Instanciate the Class.
        myoperation = getattr(mio_commando, api['operationId'])
        myoperation_inst = myoperation(self.cbacker)
        
        # Attribute the parameters to be passed to script.
        if kwargs['data'] == {}:
            data = {}
        else:
            data = json.loads(kwargs['data'])
        data = DotDict(data)
        pass_args = DotDict({
            'parameters': data,
            'query': kwargs['params'],
            'method': args[0],
            'endpoint': args[1],
            'target': self.target
        })

        # Return class execution
        try:
            result = myoperation_inst.execute(pass_args)
        except AttributeError as error:
            msg = 'Error executing custom script, please debug it... ' + str(error)
            raise RbkcliException.ApiHandlerError(msg + '\n')

        return json.dumps(result, indent=2)

class RbkCliBlackOps():
    def __init__(self, call_backer):
        self.rbkcli = call_backer
        self.request = DotDict({
              'parameter': {},
              'filter': None,
              'version': '',
              'context': None,
              'table': False,
              'select': None,
              'list': False,
              'query': '',
              'method': 'post',
              'api_endpoint': [],
              'loop': None,
              'pretty_print': False,
              'info': False,
              'documentation': False
        })


class CustomizerControls():
    def __init__(self, tools):
        self.tools = tools
        # Define the path to search.
        self.meta_api = DotDict()
        self.scripts_folder = CONSTANTS.BASE_FOLDER + '/scripts'

    def _update_env_file(self, file):
        file_dict = self.tools.load_json_file(file)
        self._gen_docs()
        file_dict['apis']['scripts'] = self.endpoints
        self.tools.create_json_file(file_dict, file)

    def sync_scripts(self, kwargs):
        target_folder = kwargs['target_folder']
        self._update_env_file(target_folder+'/me.json')
        return {'result': 'Applied scripts to environment configuration.'}

    def list_scripts(self, kwargs):
        self._gen_docs()
        return json.dumps(self.scripts_list, indent=2)

    def _gen_docs(self):
        """Create static API documentation and store to class var."""

        # The static content defined here mimics and can easily be converted
        # to a swagger file documentation. Possibly converting the Rbkcli to
        # a API server.

        self.meta_api.doc = {
            'definitions': {},
            'paths': {}
            }
        self.scripts_list = []

        #search_path = '/tmp'
    
        # Define classes that are instantiable:
        intantiable_class = '(<class \'rbkcli.core.handlers.customizer.RbkCliBlackOps'
        # Get liat of folders in the path.
        scripts_paths = [x[0] for x in os.walk(self.scripts_folder)]
        # Iterate each folder.
        for path in scripts_paths:
            # Get a list of modules inside the folder.
            module_path = [x[1] for x in pkgutil.iter_modules(path=[path])]
            # Iterate each module.
            for script in module_path:
                # Make path tangible
                sys.path.append(path)
                # Import module in the path.
                script_module = importlib.import_module(script)
                # Get objects from the module. 
                script_members = inspect.getmembers(script_module)
                # Iterate members of module.
                for member in script_members:
                    member_desc = str(member[1])
                    # Verify members that are a class.
                    if member_desc.startswith('<class '):
                        # Copy the class into a object.
                        myoperation = getattr(script_module, member[0])
                        class_base = str(myoperation.__bases__)
                        # If the parent of th e class is a instantiable class
                        if class_base.startswith(intantiable_class):
                            # Create dictionary from script members
                            script_dict = {}
                            # Attribute values to dict
                            for line in script_members:
                                key, value = line
                                script_dict[key] = value
                            
                            # Instantiate a object of the class.
                            instance = myoperation('')

                            # Attribute values to the instance for doc gen.
                            script = {}
                            instance.module = script_dict['__name__']
                            script['module'] = instance.module
                            instance.file = script_dict['__file__']
                            script['file'] = instance.file
                            instance.class_name = member[0]
                            script['class_name'] = instance.class_name
                            script['endpoint'] = instance.endpoint
                            script['method'] = instance.method

                            self.scripts_list.append(script)

                            # Generate documentation
                            self._gen_doc_script(instance)
        
        # Attribute all documentation generated to endpoints.
        self.endpoints = self.meta_api.doc

    def _gen_doc_script(self, instance):
        self.meta_api.doc['paths'][instance.endpoint] = {
        instance.method: {
            'description': instance.description,
            'operationId': instance.class_name,
            'source': instance.file,
            'operation': instance.module,
            'parameters': instance.parameters,
            'responses': {
                '200': {
                    'description': '',
                    'schema': {},
                    'table_order': [],
                    'multiple_output': ''
                }
            },
            'summary': instance.summary,
            'tags': '',
            'x-group': ''
            }
        }
