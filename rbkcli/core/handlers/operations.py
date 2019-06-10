"""Operations Handler module for rbkcli."""

from rbkcli.core.handlers import ApiTargetTools, RbkcliResponse
from rbkcli.core.handlers.meta import MetaCmds
from rbkcli.core.handlers.cmdlets import Cmdlets
from rbkcli.core.handlers.customizer import Customizer


class OperationsHandler(ApiTargetTools):
    """Handle all the API and endpoint listing, instantiates ApiHandlers."""

    class Decorators():
        """Decorators that share the OperationsHandlers variables."""

        @classmethod
        def version_looper(cls, func):
            """Loop apis versions available/supported."""
            def inner_loop(self, *args):
                """Loop version and return dictionary with results."""
                # Dictionary defined as a dot_dict for easy management.
                result = {}
                for value in self.apis_to_instantiate:
                    result[value] = func(self, value, *args)
                return result

            return inner_loop

        def verified(self, func):
            """Place holder for future implementation."""

    def __init__(self, base_kit, apis_to_instantiate):
        """Initialize Operations Handler class."""
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

        # Declare req dictionary for requests received.
        self.req = None

        # Assign the Api versions (list) to be instantiated with handlers.
        self.apis_to_instantiate = apis_to_instantiate
        self.instantiated_api_versions = []

        # Perform the instantiation.
        self._instantiate_api_handlers()

        # Perform rbkcli meta instantiation.
        self._instantiate_rbkcli_handler()

    def _instantiate_rbkcli_handler(self):
        """Instantiate the rbckcli handler to act as a imported API."""
        version = 'scripts'
        self.handler[version] = Customizer(self.user_profile,
                                           self.base_kit)
        version = 'cmdlets'
        self.handler[version] = Cmdlets(self.user_profile,
                                         self.base_kit)

        version = 'rbkcli'
        self.handler[version] = MetaCmds(self.user_profile,
                                         self.base_kit)

    @Decorators.version_looper
    def _instantiate_api_handlers(self, *version):
        """Instantiate Api Handlers from base module."""
        # Avoid linting issues
        version = version[0]

        # Loop through list of predefined apis to instantiate the versions.
        self.handler[version] = self.api_handler(self.auth, version)

    @Decorators.version_looper
    def export_apis(self, *args):
        """Export to handlers, provided the apis previously loaded."""
        # Avoid linting issues
        version = args[0]
        loaded_apis = args[1]

        # Get loaded API as external dict argument and load to handler.
        self.handler[version].endpoints = loaded_apis[version]

        # Generate endpoints list for command execution.
        self.handler[version].gen_authorization_lists()

        # Create list of successfully instantiated API.
        self.instantiated_api_versions.append(version)

    @Decorators.version_looper
    def import_apis(self, *version):
        """Import the Apis that were instantiated."""
        # Avoid linting issues
        version = version[0]

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
        """Generate list of all available operations for target."""
        # Loop through versions and create full list and a list based in the
        # user profile.
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
        #self.handler['cmdlets'].store_all_ops(self.ops)
        self.handler['rbkcli'].store_all_ops(self.ops)

        # Log Successfull action.
        msg = str('Target # Successfully generated list of authorized '
                  'endpoints for user profile: [' + self.user_profile + ']')
        self.rbkcli_logger.debug(msg)

    def _apply_whitelist(self):
        """Apply changes from whitelist in config file to ops list."""
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
        """Apply changes from blacklist in config file to ops list."""
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
        """Request execution of operation to ApiHandler."""
        # Attribute request dictionary.
        self.req = req

        # Simplify variables to pass to handler.
        final_endpoint = str(self.req.endpoint + self.req.inline_query +
                             self.req.param)
        version = self.req.version
        end_k = self.req.endpoint_key[0]

        # Call handler execute_api method for the request provided.
        api_result = self.handler[version].execute_api(self.req.method,
                                                       final_endpoint,
                                                       endpoint_key=end_k,
                                                       params=self.req.param,
                                                       data=self.req.data)

        # Return the result of API request.
        return api_result

    @RbkcliResponse.successfull_response
    def documentation(self, req):
        """Request execution of documentation to ApiHandler."""
        # Attribute request dictionary.
        self.req = req

        # Retrieving the documentation information from API handler.
        endpoint_paths = self.handler[self.req.version].endpoints['paths']
        doc_result = endpoint_paths[self.req.endpoint_matched][self.req.method]

        # Instantiating json_ops object.
        my_json = self.json_ops(doc_result)
        definitions = self.handler[self.req.version].endpoints['definitions']

        # Using json ops to resolve references in the documentation.
        doc_result = my_json.resolve_ref(definitions, doc_result)

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
        """Request information from ApiHandler."""
        # Attribute request dictionary.
        self.req = req

        # Retrieving the documentation information from API handler.
        endpoint_paths = self.handler[self.req.version].endpoints['paths']
        doc_result = endpoint_paths[self.req.endpoint_matched][self.req.method]

        # Instantiating json_ops object.
        my_json = self.json_ops(doc_result)
        definitions = self.handler[self.req.version].endpoints['definitions']

        # Using json ops to resolve references in the documentation.
        doc_result = my_json.resolve_ref(definitions, doc_result)

        # Generating a result dictionary

        return self._gen_info_output(doc_result)

    def _gen_info_output(self, doc_result):
        """Create the information output for the CLI."""
        # Create each field with similar format and spacing.
        description = '%12s [%s]' % ('Description:', doc_result['description'])
        endpoint = '%12s [/%s%s]' % ('Endpoint:', self.req.version,
                                     self.req.endpoint_matched)
        method = '%12s [%s]' % ('Method:', self.req.method)
        parameters = '%12s [%s]' % ('Parameters:',
                                    str(len(doc_result['parameters'])))

        # Create the output variable with all fields.
        output = [description, endpoint, method, parameters]

        if doc_result['parameters'] != ['']:
            output = self._gen_parameter_output(doc_result, output)

        msg = str('%s [%s]' % ('OperationsHandler # Successfully generated '
                               'info for command requested', endpoint))
        self.rbkcli_logger.debug(msg)

        # Return output as string.
        return '\n'.join(output)

    def _gen_parameter_output(self, doc_result, output):
        """Generate the parameter output for the cmd info."""
        keys_to_use = ['name', 'description', 'required', 'in', 'type']

        # Loop the parameters to add to output.
        for params in doc_result['parameters']:

            # Validate if the keys needed exist, if does not treat it.
            params = self._secure_keys(params, keys_to_use)
            param_name = '%12s -%s' % (' ', params['name'])
            output.append(param_name)
            param_desc = '%14s %s %s.' % (' ', 'Description:',
                                          params['description'])
            output.append(param_desc)
            if not params['required']:
                require = 'NOT '
            else:
                require = ''

            # dictionary validation is needed for some cases.
            # Create simplified additional info.
            add_info = str('%14s %s This parameter is %sREQUIRED to run and '
                           'should be provided in the %s as a %s.\n' %
                           (' ', 'Additional info:', require, params['in'],
                            params['type']))

            # Append all to output.
            output.append(add_info)

        return output

    def _secure_keys(self, dict_, keys, replace='N/A'):
        """Avoid KeyValue error."""
        for key in keys:
            if key not in dict_.keys():
                msg = str('OperationsHandler # There are keys that had to be'
                          ' secured')
                self.rbkcli_logger.debug(msg)
                dict_[key] = replace
        return dict_