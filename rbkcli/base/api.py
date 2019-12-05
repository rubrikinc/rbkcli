"""API base class for rbkcli."""

import base64
import json
import sys

import requests
import urllib3

from rbkcli.base.essentials import CONSTANTS, DotDict, RbkcliException
from rbkcli.base.tools import RbkcliTools


class ApiRequester:
    """Customize API requests."""

    PROTOCOL = 'https'
    DEFAULT_URL = '/api'
    PORT = ''
    VERIFICATION = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class Decorators:
        """Decorators that share the ApiHandlers variables."""

        @classmethod
        def auth_verifier(cls, func):
            """Verify the auth vars received for consistency."""
            def verify_auth(self, *args, **kwargs):
                """Verify server, username and password by calling fn."""
                # These verification should be added before any-
                # authentication is performed.
                tmp_tools = RbkcliTools(self.logger,
                                        conf_dict=CONSTANTS.CONF_DICT)
                if not tmp_tools.verify_auth_consistency(self.auth):
                    self.auth = tmp_tools.load_interactive_auth(self.auth)

                return func(self, *args, **kwargs)

            return verify_auth

        def verified(self, func):
            """Place holder for future implementation."""

    def __init__(self, logger, user_profile, auth=None):
        """Initialize API requester."""
        self.logger = logger
        self.auth = auth
        if auth is None:
            self.auth = {}
        self.url = ''
        self.api_result = requests.Response()
        self.user_profile = user_profile
        self.auth_prpt = DotDict()
        self.auth_prpt.type_ = ''
        self.auth_prpt.header = ''
        self.auth_prpt.primary_exception = ''
        self.python_version = sys.version.split("(")[0].strip()
        self.rbkcli_version = '1.0.0b3'

    @Decorators.auth_verifier
    def demand(self, method, endpoint, data=None, params=None):
        """Perform API request with provided data."""
        self._create_url(endpoint)
        self._create_auth_header()

        try:
            self.api_result = requests.request(method,
                                               self.url,
                                               params=params,
                                               data=data,
                                               headers=self.auth_prpt.header,
                                               verify=self.VERIFICATION)

            self._validate_token_auth(method, endpoint, data={}, params={})

        except requests.exceptions.ConnectionError as error:
            self.logger.error('ApiRequesterError # ' + str(error))
            raise RbkcliException.ApiRequesterError(str(error))

        except requests.exceptions.InvalidURL as error:
            self.logger.print_error('ApiRequesterError # ' + str(error))
            raise RbkcliException.ApiRequesterError(str(error))

        return self.api_result

    def demand_json(self, method, endpoint, data=None):
        """Call demand method and only return json data."""
        try:
            self.demand(method, endpoint, data)
            json_data = json.loads(self.api_result.text)

        except json.decoder.JSONDecodeError as error:
            msg = '%s %s "%s"' % ('Invalid json data received.', str(error),
                                  self.api_result.text)
            self.logger.error('ApiRequesterError # ' + msg)
            raise RbkcliException.ApiRequesterError(msg)

        return json.dumps(json_data, indent=2, sort_keys=True)

    def _create_url(self, endpoint):
        """Concatenate the URL for the request."""
        self.url = '%s://%s%s%s%s' % (self.PROTOCOL, self.auth.server,
                                      self.PORT, self.DEFAULT_URL, endpoint)

    def _create_auth_header(self):
        """Create the auth header based on auth type (user/token)."""
        user_agent = "rbkcli--{}--{}".format(self.rbkcli_version,
                                             self.python_version)
        try:
            auth = 'Bearer ' + self.auth.token
            self.auth_prpt.type_ = 'token'
            if self.auth_prpt.primary_exception != '':
                raise RbkcliException.ToolsError(
                    self.auth_prpt.primary_exception)
        except KeyError as bad_key:
            msg = ('Authorization key not found ' + str(bad_key))
            auth = self._create_username_header(msg)
        # Fix or cleanup needed.
        except AttributeError as bad_key:
            msg = ('Authorization key not found ' + str(bad_key))
            auth = self._create_username_header(msg)
        # Until here
        except RbkcliException.ToolsError as error:
            auth = self._create_username_header(error)

        self.auth_prpt.header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': user_agent,
            'Authorization': auth,
        }

    def _create_username_header(self, msg):
        """Create the username authentication header for API request."""
        self.logger.warning('ApiRequester # ' + msg)
        try:
            credentials = ('%s:%s' % (self.auth.username,
                                      self.auth.password))
            # Python 2 compatibility
            try:
                base64bytes = base64.encodebytes(credentials.encode('utf-8'))
            except AttributeError:
                base64bytes = base64.b64encode(credentials.encode('utf-8'))

            auth = 'Basic ' + base64bytes.decode('utf-8').replace('\n', '')
            self.auth_prpt.type_ = 'username'
        except KeyError as bad_key:
            msg = ('%s%s%s.' % (self.auth_prpt.primary_exception,
                                ' Expected authorization key not found ',
                                str(bad_key)))
            msg = msg.strip(' ')
            self.logger.error('%s%s' % ('ApiRequesterError # ', msg))
            raise RbkcliException.ApiRequesterError(msg)
        return auth

    def _validate_token_auth(self, method, endpoint, data, params):
        """Validate last token authentication."""
        error_msg = 'The supplied authentication is invalid'
        error_msg2 = '"message":"Incorrect username/password"'
        if (self.api_result.text == error_msg and
                self.auth_prpt.type_ == 'token'):
            error_msg = 'The supplied TOKEN authentication is invalid.'
            self.auth_prpt.primary_exception = error_msg
            error_msg = '%s %s' % (error_msg, 'Attempting to use secondary'
                                   ' auth type (username/password).')
            self.logger.warning('ApiRequester # ' + error_msg)

            self.demand(method, endpoint, data, params)
        elif (error_msg2 in self.api_result.text and
              self.auth_prpt.type_ == 'username'):
            error_msg = 'The supplied authentication is invalid'
            self.logger.error('ApiRequester # ' + error_msg)
            error_msg = error_msg + '.\n'
            raise RbkcliException.ApiRequesterError(error_msg)
        else:
            # Log successful actions
            msg = '%s [%s:%s]' % ('ApiRequester # Successfully requested API',
                                  method,
                                  self.url)
            self.logger.debug(msg)


class RubrikApiHandler:
    """Define methods to execute the APIs."""

    def __init__(self, logger, auth, version, user_profile='admin'):
        """Initialize Rbkcli Executor."""
        self._verify_api_version(version)
        self.local_tools = DotDict({})
        self.local_tools.logger = logger
        self.local_tools.auth = auth
        self.local_tools.user_profile = user_profile

        self.version = version

        self.endpoints = {}
        self._assign_methods()
        self.filter_lists = DotDict({})
        self.focus_list = []

    def _verify_api_version(self, version):
        """Verify the provided API version."""
        if version not in CONSTANTS.SUPPORTED_API_VERSIONS:
            msg = str('API version [' + version + '] does not match any '
                      'accepted version.')
            error = 'ApiHandlerError # ' + msg
            self.local_tools.logger.error(msg)
            raise RbkcliException.ApiHandlerError(error)

    def _assign_methods(self):
        """Assign the correct import and execute method based in version."""
        if self.version in ('v1', 'v2', 'internal'):
            self.import_api = self._download_api_doc
            self.execute_api = self.api_requester
        else:
            self.import_api = self._temp_import

    def _download_api_doc(self):
        """Download the swagger api-doc file from server."""
        try:
            url = str('https://%s/docs/%s/api-docs' %
                      (self.local_tools.auth.server,
                       self.version))
            tmp_tools = RbkcliTools(self.local_tools.logger)
            content = tmp_tools.download_file(url)
            content_dict = tmp_tools.yaml_load(content)
            self.endpoints = {
                'paths': content_dict['paths'],
                'definitions': content_dict['definitions']
            }
        except RbkcliException.ToolsError as error:
            msg = '%s [%s]. %s' % ('ApiHandlerError # Unable to download API',
                                   self.version,
                                   error)
            self.local_tools.logger.error(msg)

        return self.endpoints

    def api_requester(self, *args, **kwargs):
        """Instantiate requester and request API."""
        method, endpoint = args
        endpoint_key = kwargs['endpoint_key']
        data = kwargs['data']
        params = kwargs['params']

        if self.focus_list != [] and endpoint_key not in self.focus_list:
            msg = str('Requested endpoint [' + endpoint_key + '] not found on'
                      ' authorized endpoints list.')
            raise RbkcliException.ApiHandlerError(str(msg))

        endpoint = '/%s/%s' % (self.version, endpoint)
        api_rs = ApiRequester(self.local_tools.logger,
                              self.local_tools.user_profile,
                              auth=self.local_tools.auth).demand(method,
                                                                 endpoint,
                                                                 data=data,
                                                                 params=params)
        return api_rs

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

        self.focus_list = self.filter_lists[self.local_tools.user_profile]

    def _create_all_methods_list(self, field='summary', string='TOKEN'):
        """Generate simplified list of paths and methods."""
        filter_list = []
        string_ = string.replace(' ', '_')

        for endpoint, endpoint_data in self.endpoints['paths'].items():
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

    def _temp_import(self):
        """Place holder import for unpredicted API versions."""
        msg = 'ApiHandlerError # Api version not supported.'
        self.local_tools.logger.error(msg)
        return {}
