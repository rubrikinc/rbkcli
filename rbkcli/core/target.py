"""API targets module for rbkcli."""

import copy

from rbkcli.base import CONSTANTS, RbkcliBase
from rbkcli.core.handlers.environment import EnvironmentHandler
from rbkcli.core.handlers.inputs import InputHandler
from rbkcli.core.handlers.outputs import OutputHandler


class ApiTarget(RbkcliBase):
    """Define the Target to which we will request APIs from."""

    def __init__(self, ctx, auth=None, env=None):
        """Initialize Rbkcli Rubrik Cluster."""
        self.ctx = self.dot_dict(ctx)

        # Verify base folder provided.
        if self.ctx.base_folder == '':
            self.ctx.base_folder = CONSTANTS.BASE_FOLDER

        # Make sure the parent init is run.
        RbkcliBase.__init__(self, user_profile=self.ctx.user_profile,
                            base_folder=self.ctx.base_folder,
                            workflow=self.ctx.workflow)

        # req is a dict created from te raw input of API request.
        self.req = {}
        self.ini_req = {}

        # Set workflow to instance variable
        # Load the API target from tools.
        self.tools = self.tools()
        if auth in (None, {}):
            self.auth = self.tools.load_auth()
        else:
            self.auth = self.dot_dict(auth)

        base_kit = self._gen_base_kit()

        # Load or create environment based on imported apis
        self.environment = env
        if self.environment is None:
            self.environment = EnvironmentHandler(base_kit)

        # Instantiate operations and api handlers
        self.operations = self.environment.evaluate()

        base_kit.target_folder = self.environment.env.folder

        # Instantiate InpuHandler for future use
        self.validator = InputHandler(base_kit, self.operations)

        self.operations.handler.cmdlets.initialize_callbacker(self.operations)
        self.operations.handler.scripts.initialize_callbacker(self.operations)

        self.formatter = OutputHandler(base_kit, self.operations)

    def execute(self, **kwargs):
        """Call the execute method for the provided request."""
        # Generate a dictionary of the data passed for request
        self._gen_req_dict(kwargs)

        # Use input handler to validate the data entered.
        # If any error to be raised related to request inconsistency,
        # should come from this
        self.req = self.validator.validate(self.ini_req)

        # Once input is normalize pass it on to request the operation.
        return self.operations.execute(self.req)

    def documentation(self, **kwargs):
        """Call the documentation method for the provided request."""
        # Generate a dictionary of the data passed for request
        self._gen_req_dict(kwargs)

        # Use input handler to validate the data entered.
        # If any error to be raised related to request inconsistency,
        # should come from this
        self.req = self.validator.validate(self.ini_req)

        # Once input is normalize pass it on to request the operation.
        return self.operations.documentation(self.req)

    def information(self, **kwargs):
        """Call the information method for the provided request."""
        # Generate a dictionary of the data passed for request
        self._gen_req_dict(kwargs)

        # Use input handler to validate the data entered.
        # If any error to be raised related to request inconsistency,
        # should come from this
        self.req = self.validator.validate(self.ini_req)

        # Once input is normalize pass it on to request the operation.
        return self.operations.information(self.req)

    def command(self, **kwargs):
        """Call the information method for the provided request."""
        # Generate a dictionary of the data passed for request
        self._gen_req_dict(kwargs)
        result = self.dot_dict()
        #print(self.req)

        # Converting endpoint to a list.
        if isinstance(self.req.api_endpoint, str):
            self.req.api_endpoint = [self.req.api_endpoint]

        # Normalizing request dictionary
        self.req.endpoint = ' '.join(self.req.api_endpoint)
        self.req.formatt = 'raw'
        self.req.param = self.req.query
        self.req.data = self.req.parameter

        #self.ini_req = copy.deepcopy(self.req)
        for key, value in self.req.items():
            self.ini_req[key] = value
        # Get the documentation string for every API run.
        self.req.documentation_objct = self.documentation(args=self.req).text

        ## FIX
        ### print(self.req.output_workflow)

        # If info requested, only print info.
        if self.req.info:
            result = self.information(args=self.req)
        # If documentation requested, only print documentation.
        elif self.req.documentation:
            result.text = self.req.documentation_objct
        # If available keys requested get the available keys.
        elif self.req.output_workflow != []:
            if '?' in self.req.output_workflow[0]['value']:
                result.text = self.formatter.available_fields(self.req)
                self.req.output_workflow.pop(0)
            else:
                result = self.execute(args=self.req)
        else:
            result = self.execute(args=self.req)

        return self.formatter.outputfy(self.req, result)
        #return result

    def _gen_req_dict(self, kwargs):
        """Generate the request dictionary to be passed."""
        # Create the dictionary as a dot ddict for easy access.
        if self.req == {}:
            self.req = self.dot_dict()
            self.ini_req = self.dot_dict()
        kwargs = kwargs['args']
        for key in kwargs.keys():
            self.req[key] = kwargs[key]

    def _gen_base_kit(self):
        """Generate a shared context to pass to other classes."""
        # Create the dictionary as a dot ddict for easy access.
        base_kit = self.dot_dict()
        base_kit.config_dict = self.conf_dict
        base_kit.base_folder = self.ctx.base_folder
        base_kit.tools = self.tools
        base_kit.logger = self.rbkcli_logger
        base_kit.dot_dict = self.dot_dict
        base_kit.target = self.auth.server
        base_kit.api_handler = self.api_handler
        base_kit.discover_fn = self.ctx.discover_fn
        base_kit.auth = self.auth
        base_kit.user_profile = self.ctx.user_profile
        base_kit.json_ops = self.json_ops
        base_kit.workflow = self.ctx.workflow
        #base_kit.target_folder = self.environment.env.folder

        ### Test here
        callback_kit = self.dot_dict()
        base_kit.callback_cmd = self.command
        base_kit.parser = self.ctx.parser

        return base_kit


class RubrikCluster(ApiTarget):
    """
    Class to instanciate a API target.

    Which is specifically a Rubrik Cluster, has a dicovery_action for the
    target that could be different per target type.
    """

    def __init__(self, ctx, auth=None, env=None):
        """Initialize Rbkcli Rubrik Cluster."""
        ctx['discover_fn'] = self._discovery_action
        #print('RubrikCluster:' + str(auth))
        ApiTarget.__init__(self, ctx, auth=auth, env=env)

    def _discovery_action(self):
        """Gather cluster and nodes data, returns list of dict."""
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
            target_resolution.envId = cluster_dict['id']
            target_resolution.envName = cluster_dict['name']
            target_resolution.id = node['id']
            target_resolution.ip = node['ipAddress']
            resolution_data.append(target_resolution)
            target_resolution = self.dot_dict()

        return resolution_data


class RbkcliTarget():
    """
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

    """

    def __init__(self, ctx, auth=None, env=None):
        """Initialize RbkcliTarget class."""
        #print('RbkcliTarget:' + str(auth))
        # Attribute the to instance var the instantiation of a Cluster.
        self.target = RubrikCluster(ctx,
                                    auth=auth,
                                    env=env)

    def add_target(self):
        """Future method to dynamically add targets to the rbkcli execution."""

    def remove_target(self):
        """Future method to dynamically rmv targets to the rbkcli execution."""