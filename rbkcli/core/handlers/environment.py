"""Environment handler module for rbkcli."""

import os

from rbkcli.base import CONSTANTS, RbkcliException
from rbkcli.core.handlers import ApiTargetTools
from rbkcli.core.handlers.operations import OperationsHandler


class EnvironmentHandler(ApiTargetTools):
    """
    Handle all actions related to the environment.

    Actions such as load, create, node resolution, me.json creation.
    """

    def __init__(self, base_kit):
        """Initialize EnvironmentHandler class."""
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
        self.operations = None

    def evaluate(self):
        """
        Verify if the environment needs to be created or loaded or re-sync.

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
        """
        # Either will load the self.env.details

        if not self.load():

            # Add prevention for interaction for autocomplete workflow.
            if self.base_kit.workflow == 'complete':
                return []
            self.rbkcli_logger.print_warning('EnvironmentHandler # No cached'
                                             ' API found for this target, '
                                             'importing APIs...')
            if not self.create():
                self.rbkcli_logger.print_error('EnvironmentHandlerError # '
                                               'Unable to create cached '
                                               'environment for target.')
                raise Exception

        # Once the environment is successfully loaded the available -
        # operations are generated.
        self.operations.generate_ops()

        return self.operations

    def load(self):
        """Load the environmental files."""
        # Performs resolution verification and best effort fixing.
        if not self._is_resolvable():
            return False

        # _is_resolvable will load the env_id which is the target folder name.
        if not self._is_loadable():
            return False

        # if not self._is_current():
        #    return False

        # Will get the APIs from the file and instantiate a Operation.
        if not self._is_exportable():
            return False

        return True

    def _is_resolvable(self):
        """Check if resolution file exists and returns valid results."""
        # Attempts to load the resolution file.
        try:
            self.resolution.data = self.tools.load_json_file(
                self.resolution.file_path)
        except RbkcliException.ToolsError as error:

            # If fails log and error, attempts to recreate file.
            sufix = 'TargetError # '
            msg = str('%s%s' % (sufix, error))
            self.rbkcli_logger.error(msg)
            msg = str('%sFailed to load [%s] file, attempting'
                      ' to recreate the [%s] file.' %
                      (sufix,
                       self.resolution.file_name,
                       self.resolution.file_name))
            self.rbkcli_logger.error(msg)
            self._recreate_resolution_file()

            # After recreation tries to load again.
            try:
                self.resolution.data = self.tools.load_json_file(
                    self.resolution.file_path)

            # If it fails, return false.
            except RbkcliException.ToolsError as error:
                msg = str('%s %s.' % ('EnvironmentHandlerError # Unable to '
                                      'resolve target.', error))
                self.rbkcli_logger.debug(msg)
                return False

        # Finally try to resolve target, returns True or False.
        return self._is_resolved()

    def _is_resolved(self):
        """
        Resolve target ubti a cached environment.

        With the resolution data received attemps to resolve target into a
        known environment ID.
        """
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
                              self.env.id + ']')
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
        """Check if me file exists and returns valid results."""
        # Allow reuse of the function by allowing to pass existing file.
        if file_path != '':
            self.env.file_path = file_path
        else:
            # Build the paths to the environment file to load.
            self.env.folder = CONSTANTS.TARGETS_FOLDER + '/' + self.env.id
            self.base_kit.target_folder = self.env.folder
            self.env.file_path = self.env.folder + '/' + self.env.file_name

        # Attempt to loas the environment file.
        try:
            file_dict = self.tools.load_json_file(self.env.file_path)
            for key, value in file_dict.items():
                self.env[key] = value

        # If it fails logs an error and returs False.
        except RbkcliException.ToolsError as error:
            sufix = 'TargetError # '
            msg = str('%s%s' % (sufix, error))
            self.rbkcli_logger.error(msg)
            msg = str('%sFailed to load [%s] environment file, will attempt '
                      'to download API docs and create a new [%s].' %
                      (sufix, self.env.file_name, self.env.file_name))
            self.rbkcli_logger.error(msg)
            return False

        # Assuming it succeeds, logs successfull loading action.
        msg = str('Target # Successfully loaded environment file: [' +
                  self.env.file_name + ']')
        self.rbkcli_logger.debug(msg)

        # Assuming it succeeds, return if what is loaded is valid.
        return self._is_valid()

    def _is_valid(self):
        """Verify bare minimun requirements for a env file."""
        # Checks if env file contains the needed keys.
        msg = str('Target # Successfully verified keys in environment file:'
                  ' [' + self.env.file_name + ']')
        self.rbkcli_logger.debug(msg)

        return True

    def _is_current(self):
        """Discover target and confirm if loaded version is current."""
        # Check this out.
        if not self._is_discoverable():
            raise Exception('Connection error')

        # Verify discovered data versus loaded data.
        # THIS CANNOT BE PERFORMED AT EVERY COMMAND.

        return True

    def _is_exportable(self):
        """Export the loaded Api data to Operations Handler."""
        self.operations = OperationsHandler(self.base_kit,
                                            self.env.imported_api_v)
        self.operations.export_apis(self.env.apis)

        # Provide APIs to metacommands for.
        self.operations.handler.rbkcli.all_apis = self.env.apis
        return True

    def create(self):
        """Create environmental file by getting uniq identifier."""
        # Based in the pre-loaded discovery dictionary:
        # Instantiate the discovery handlers.
        # Execute the discovery APIs
        if not self._is_discoverable():
            return False

        # Assumin its discovered will instantiate ApiHandlers and import APIs.
        if not self._is_importable():
            return False

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
        """Verify if target is discoverable."""
        # Runs the provided discovery action upon instantiation.
        self.discovery.results = self.discovery.action()
        self.env.discovery = self.discovery.results

        # Verify if the result is correct type and has necessary data.
        if not self._is_discovery_valid():
            return False

        # Assuming it does, loads that to the environment.
        self.env.id = self.discovery.results[0]['envId']

        # Build the paths to the environment file to create.
        self.env.folder = CONSTANTS.TARGETS_FOLDER + '/' + self.env.id
        self.env.file_path = self.env.folder + '/' + self.env.file_name

        # Assuming discovery went fine, we log and return
        msg = str('Target # All expected discovery keys are valid.')
        self.rbkcli_logger.debug(msg)
        return True

    def _is_discovery_valid(self):
        """Verify each key return for validity."""
        # Expects to receive a dictionary with 4 keys.
        if not isinstance(self.discovery.results, list):
            msg = str('EnvironmentHandlerError # Discovery results are not'
                      ' valid.')
            self.rbkcli_logger.error(msg)
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
                    if value in ('', []):
                        self.rbkcli_logger.error(msg)
                        raise Exception
                return True

            # If the key is not present log error and raise exception
            except KeyError:
                self.rbkcli_logger.error(msg)
                raise Exception

    def _is_importable(self):
        """Instantiate Operations and import Apis."""
        try:
            spt_api_v = CONSTANTS.SUPPORTED_API_VERSIONS
            self.operations = OperationsHandler(self.base_kit, spt_api_v)
            self.env.apis = self.operations.import_apis()
            self.env.imported_api_v = self.operations.instantiated_api_versions

            # Provide APIs to metacommands for listing commands.
            self.operations.handler.rbkcli.all_apis = self.env.apis

            # Checking if minimun requirement is met:
            if 'v1' not in self.env.imported_api_v:
                error = 'Unable to download basi set of APIs, please check connection to target...\n'
                raise RbkcliException.ApiHandlerError(error)
            return True
        except RbkcliException.ToolsError as error:
            msg = '%s. %s' % ('EnvironmentHandlerError # Unable to instantiate'
                              ' OperationsHandler', error)
            self.rbkcli_logger.error(msg)



    def _update_resolution_file(self):
        """Update target_resolution file with newly discovered nodes."""
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
        """Load all cached environments and recreates the resolution file."""
        # If recreation was asked, resolution data will be reloaded.
        self.resolution.data = []

        # Verify if target folders exists.
        if os.path.isdir(CONSTANTS.TARGETS_FOLDER):

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