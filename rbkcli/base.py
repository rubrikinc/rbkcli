'''Base class and tools for rbkcli.'''

import base64
import copy
from getpass import getpass
import json
import ipaddress
import logging

from logging.handlers import RotatingFileHandler

import time
import os
import sys

from uuid import UUID

import paramiko
import requests
import urllib3
import yaml


BASE_FOLDER = os.path.expanduser('~/rbkcli')
TARGETS_FOLDER = BASE_FOLDER + '/targets'
CONF_FOLDER = BASE_FOLDER + '/conf'
LOGS_FOLDER = BASE_FOLDER + '/logs'
SUPPORTED_API_VERSIONS = ['v1',
                          'v2',
                          'internal',
                          'adminCli',
                          'custom',
                          'rbkcli']
SUPPORTED_API_METHODS = ['head',
                         'get',
                         'post',
                         'put',
                         'patch',
                         'delete']
USERS_PROFILE = ['dev', 'admin', 'support']                         
SUPPORTED_USER_METHODS = {
    'admin': ['get'],
    'support': ['get'],
    'dev': SUPPORTED_API_METHODS
}
SUPPORTED_OUTPUT_FORMATS = ['raw',
                            'json',
                            'table',
                            'list',
                            'values']
CONF_DICT = {}


class DotDict(dict):
    '''Create a dictionary managed/accessed with dots.'''
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CONSTANTS = DotDict({
    'BASE_FOLDER': BASE_FOLDER,
    'TARGETS_FOLDER': TARGETS_FOLDER,
    'CONF_FOLDER': CONF_FOLDER,
    'LOGS_FOLDER': LOGS_FOLDER,
    'SUPPORTED_API_VERSIONS': SUPPORTED_API_VERSIONS,
    'SUPPORTED_API_METHODS': SUPPORTED_API_METHODS,
    'USERS_PROFILE': USERS_PROFILE,
    'SUPPORTED_USER_METHODS': SUPPORTED_USER_METHODS,
    'SUPPORTED_OUTPUT_FORMATS': SUPPORTED_OUTPUT_FORMATS,
    'CONF_DICT': CONF_DICT
})


class DynaTable():
    '''Create a dynamically sized table with summary.'''

    ROW_DIVISION_CHAR = '|'
    LINE_DIVISION_CHAR = '='

    def __init__(self, headers, rows, logger='', **kwargs):
        '''Initialize DynaTable.'''

        # Verifying if headers and rows have the same amout of objects.
        if len(headers) != len(rows) or len(headers) == 1:
            self.table = ['Error # Invalid table']

        # Assigning provided values to the class properties
        if 'ROW_DIVISION_CHAR' in kwargs.keys():
            DynaTable.ROW_DIVISION_CHAR = kwargs['ROW_DIVISION_CHAR']
        if 'LINE_DIVISION_CHAR' in kwargs.keys():
            DynaTable.LINE_DIVISION_CHAR = kwargs['LINE_DIVISION_CHAR']
        if 'summary' in kwargs.keys():
            self.summary = kwargs['summary']
        else:
            self.summary = ''

        self.logger = logger
        self.headers = headers
        self.rows = rows
        self.table = []

    def _format_rows(self):
        '''
        Based on the maximum size acquired, reformat each value of each row
        to have that size.
        '''

        try:
            rows_size = self._get_rows_size(self.headers, self.rows)
        except RbkcliException.DynaTableError:
            return False

        for i in enumerate(rows_size):
            text = self.headers[i[0]]
            size = rows_size[i[0]]
            self.headers[i[0]] = (' {text:<{size}} '.format(text=text,
                                                            size=size))
            for line in enumerate(self.rows[i[0]]):
                text = self.rows[i[0]][line[0]]
                self.rows[i[0]][line[0]] = (' {text:<{size}} '. \
                                           format(text=text, size=size))
        return True

    def assemble_table(self):
        '''
        Create and returns a 'table' list, by appending and joinning headers,
        line separator and rows.
        '''

        table = []
        line = []
        lines = []
        n_lines = len(self.rows[0])

        if not self._format_rows():
            return [str('Error: Returned data is inconsistent with table'
                        ' creation.')]
        headers = self.ROW_DIVISION_CHAR.join(self.headers)

        for i in range(n_lines):
            for line_number in self.rows:
                line.append(line_number[i])
            lines.append(self.ROW_DIVISION_CHAR.join(line))
            line = []

        line_division_size = (len(lines[0]))

        table.append(headers)
        table.append(self.LINE_DIVISION_CHAR * line_division_size)
        for linex in lines:
            table.append(linex)

        if self.summary != '':
            table.append('\n**' + self.summary + ' [' + str(n_lines) + ']')

        self.table = table

        return table

    def print_table(self):
        '''Re-assembles the table and prints it, prints the table.'''

        table = self.assemble_table()
        for i in table:
            print(i)

    def _get_rows_size(self, headers_calc, rows_calc):
        '''
        Joins all values in one list and gets the maximum size, of all
        values per row.
        '''

        rows_size = []
        for i in enumerate(headers_calc):
            try:
                rows_calc[i[0]].append(headers_calc[i[0]])
                rows_size.append(len(max(rows_calc[i[0]], key=len)))
                rows_calc[i[0]].remove(headers_calc[i[0]])
            except IndexError:
                raise RbkcliException.DynaTableError('Incorrect number of '
                                                     'rows provided')

        return rows_size


class ApiRequester():
    '''Customize API requests.'''

    PROTOCOL = 'https'
    DEFAULT_URL = '/api'
    PORT = ''
    VERIFICATION = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class Decorators():
        '''Decorators that share the ApiHandlers variables.'''

        @classmethod
        def auth_verifier(self, func):
            '''Verify the auth vars received for consistency.'''
            
            def verify_auth(self, *args, **kwargs):
                '''Verify server, username and password by calling fn.'''
                global CONF_DICT

                # These verification should be added before any-
                # authentication is performed.
                if (not RbkcliTools(self.logger,
                   conf_dict=CONF_DICT)._verify_auth_consistency(
                   self.auth)):
                    self.auth = RbkcliTools(self.logger,
                       conf_dict=CONF_DICT)._load_interactive_auth(self.auth)
                return func(self, *args, **kwargs)

            return verify_auth


    def __init__(self, logger, user_profile, auth=''):
        '''Initialize API requester.'''
        self.logger = logger
        self.auth = auth
        self.auth_header = {}
        self.url = ''
        self.api_result = requests.Response()
        self.auth_type = ''
        self.primary_auth_exception = ''
        self.user_profile = user_profile

    @Decorators.auth_verifier
    def demand(self, method, enpoint, data={}, params={}):
        '''Perform API request with provided data.'''
        self._create_url(enpoint)
        self._create_auth_header()

        try:
            self.api_result = requests.request(method,
                                               self.url,
                                               params=params,
                                               data=data,
                                               headers=self.auth_header,
                                               verify=self.VERIFICATION)

            self._validate_token_auth(method, enpoint, data={}, params={})

        except requests.exceptions.ConnectionError as error:
            self.logger.error('ApiRequesterError # ' + str(error))
            raise RbkcliException.ApiRequesterError(str(error))

        except requests.exceptions.InvalidURL as error:
            self.logger.print_error('ApiRequesterError # ' + str(error))
            raise RbkcliException.ApiRequesterError(str(error))
            
        return self.api_result

    def demand_json(self, method, enpoint, data={}):
        '''Call demand method and only return json data.'''
        try:
            self.demand(method, enpoint, data)
            json_data = json.loads(self.api_result.text)

        except json.decoder.JSONDecodeError as error:
            msg = '%s %s "%s"' % ('Invalid json data received.', str(error),
                                  self.api_result.text)
            self.logger.error('ApiRequesterError # ' + msg)
            raise RbkcliException.ApiRequesterError(msg)

        return json.dumps(json_data, indent=2, sort_keys=True)

    def _create_url(self, enpoint):
        '''Concatenate the URL for the request.'''
        self.url = '%s://%s%s%s%s' % (self.PROTOCOL, self.auth.server,
                                      self.PORT, self.DEFAULT_URL, enpoint)

    def _create_auth_header(self):
        '''Create the auth header based on auth type (user/token).'''
        try:
            auth = 'Bearer '+ self.auth.token
            self.auth_type = 'token'
            if self.primary_auth_exception != '':
                raise RbkcliException.ToolsError(self.primary_auth_exception)
        except KeyError as bad_key:
            msg = ('Authorization key not found ' + str(bad_key))
            auth = self._create_username_header(msg)
        except RbkcliException.ToolsError as error:
            auth = self._create_username_header(error)

        self.auth_header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': auth,
            }

    def _create_username_header(self, msg):
        '''Create the username authentication header for API request.'''
        self.logger.warning('ApiRequester # ' + msg)
        try:
            credentials = ('%s:%s' % (self.auth.username,
                                      self.auth.password))
            base64bytes = base64.encodebytes(credentials.encode('utf-8'))
            auth = 'Basic ' + base64bytes.decode('utf-8').replace('\n', '')
            self.auth_type = 'username'
        except KeyError as bad_key:
            msg = ('%s%s%s.' % (self.primary_auth_exception,
                                ' Expected authorization key not found ',
                                str(bad_key)))
            msg = msg.strip(' ')
            self.logger.error('%s%s' % ('ApiRequesterError # ', msg))
            raise RbkcliException.ApiRequesterError(msg)
        return auth

    def _validate_token_auth(self, method, enpoint, data, params):
        '''Validate last token authentication.'''
        error_msg = 'The supplied authentication is invalid'
        error_msg2 = '"message":"Incorrect username/password"'
        if self.api_result.text == error_msg and self.auth_type == 'token':
            error_msg = 'The supplied TOKEN authentication is invalid.'
            self.primary_auth_exception = error_msg
            error_msg = '%s %s' % (error_msg, 'Attempting to use secondary'
                                   ' auth type (username/password).')
            self.logger.warning('ApiRequester # ' + error_msg)
            #del self.auth.token
            self.demand(method, enpoint, data, params)
        elif error_msg2 in self.api_result.text and self.auth_type == 'username':
            error_msg = 'The supplied authentication is invalid'
            self.logger.error('ApiRequester # ' + error_msg)
            raise RbkcliException.ApiRequesterError(error_msg)
        else:
            # Log successfull actions
            msg = '%s [%s:%s]' % ('ApiRequester # Successfully requested API',
                                  method,
                                  self.url)
            self.logger.debug(msg)


class RubrikApiHandler():
    '''Define methods to execute the APIs'''

    def __init__(self, logger, auth, version, user_profile='admin'):
        '''Initialize Rbkcli Executor.'''
        self.accepted_versions = SUPPORTED_API_VERSIONS
        self._verify_api_version(version)
        self.logger = logger
        self.version = version
        self.auth = auth
        self.endpoints = {}
        self._assign_methods()
        self.filter_lists = DotDict({})
        self.focus_list = []
        self.user_profile = user_profile

    def _verify_api_version(self, version):
        '''Verify the provided API version.'''
        if version not in self.accepted_versions:
            msg = str('API version [' + version + '] does not match any '
                      'accepted verison.')
            raise RbkcliException.ApiHandlerError()

    def _assign_methods(self):
        '''Assing the correct import and execute method based in version.'''
        if self.version in ('v1', 'v2', 'internal'):
            self.import_api = self._download_api_doc
            self.execute_api = self._api_requester
        else:
            self.import_api = self._temp_import

    def _download_api_doc(self):
        '''Download the swagger api-doc file from server.'''
        try:
            url = 'https://%s/docs/%s/api-docs' % (self.auth.server,
                                                   self.version)
            content = RbkcliTools(self.logger).download_file(url)
            content_dict = RbkcliTools(self.logger).yaml_load(content)
            self.endpoints = {
                'paths': content_dict['paths'],
                'definitions': content_dict['definitions']
            }
        except RbkcliException.ToolsError as error:
            msg = '%s [%s]. %s' % ('ApiHandlerError # Unable to download API',
                                   self.version,
                                   error)
            self.logger.error(msg)
            
        return self.endpoints

    def _api_requester(self, method, enpoint, endpoint_key='?', data={},
                       params={}):
        '''.'''
        #endpoint_validation = '%s:%s:' % (enpoint, method)

        if self.focus_list != [] and endpoint_key not in self.focus_list:
            msg = str('Requested endpoint [' + endpoint_key + '] not found on'
                      ' authorized endpoints list.')
            raise RbkcliException.ApiHandlerError(str(msg))
            
        else:
            enpoint = '/%s/%s' % (self.version, enpoint)
            api_result = ApiRequester(self.logger, self.user_profile,
                                      auth=self.auth).demand(method,
                                                             enpoint,
                                                             data=data,
                                                             params=params)
        return api_result

    def gen_authorization_lists(self):
        '''
        Create custom lists of authorized based in the user profile
        that was instantiated.
        The focus list is used to verify if the API can be executed or not.
        '''
        filter_list = self._create_all_methods_list(string='REQUIRES SUPPORT'
                                                    ' TOKEN')

        for user in USERS_PROFILE:
            self.filter_lists[user] = []
            requires = ''
            if user == 'admin':
                requires = 'NA'
            for method in SUPPORTED_USER_METHODS[user]:
                for method_line in filter_list:
                    if str(':%s:%s' % (method, requires)) in method_line:
                         self.filter_lists[user].append(method_line)

        for user, filter_list in self.filter_lists.items():
            filter_list.sort()

        self.focus_list = self.filter_lists[self.user_profile]

    def _create_all_methods_list(self, field='summary', string='TOKEN'):
        '''.'''
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
        '''.'''
        return {}


class RbkcliException(Exception):
    '''Customize Rbkcli exceptions.'''

    class ApiRequesterError(Exception):
        '''Customize DynaTable exceptions.'''

    class DynaTableError(Exception):
        '''Customize DynaTable exceptions.'''

    class ToolsError(Exception):
        '''Customize RbkcliTools exceptions.'''

    class LoggerError(Exception):
        '''Customize RbkcliLogger exceptions.'''

    class ClusterError(Exception):
        '''Customize RbkcliLogger exceptions.'''

    class ApiHandlerError(Exception):
        '''Customize DynaTable exceptions.'''

    class RbkcliError(Exception):
        '''Customize DynaTable exceptions.'''


class RbkcliLogger():
    '''Customize logger.'''
    def __init__(self, log_name, module, mode=''):
        '''Initialize logger.'''
        self.module = module
        self.logger = logging.getLogger('rbkcli')
        self.logger.status = 'creating'

        self._validate_log_folder(log_name)
        self._configure_logger(log_name, mode)

    def error(self, msg):
        '''Log an error msg to file.'''
        self.logger.error(msg)

    def info(self, msg):
        '''Log an info msg to file.'''
        self.logger.info(msg)

    def debug(self, msg):
        '''Log a debug msg to file..'''
        self.logger.debug(msg)

    def exception(self, msg):
        '''Log an exception msg to file..'''
        self.logger.exception(msg)

    def warning(self, msg):
        '''Log an warning msg to file..'''
        self.logger.warning(msg)

    def print_error(self, msg):
        '''Log and print an error msg to file.'''
        print(msg)
        self.logger.error(msg)

    def print_info(self, msg):
        '''Log and print an info msg to file.'''
        print(msg)
        self.logger.info(msg)

    def print_debug(self, msg):
        '''Log and print a debug msg to file..'''
        print(msg)
        self.logger.debug(msg)

    def print_exception(self, msg):
        '''Log and print an exception msg to file..'''
        print(msg)
        self.logger.exception(msg)

    def print_warning(self, msg):
        '''Log and print an warning msg to file..'''
        print(msg)
        self.logger.warning(msg)

    def _validate_log_folder(self, log_name):
        '''Validate the folder provided, if does not exist, create it.'''
        try:
            if not os.path.isfile(log_name):
                raise FileNotFoundError(log_name)
        except FileNotFoundError as error:
            folder = log_name.strip().split('/')
            folder.pop(-1)
            folder = '/'.join(folder)
            RbkcliTools(self.logger).safe_create_folder(folder)

    def _configure_logger(self, log_name, mode):
        '''Configure logger with console and file handling.'''
        formatted = logging.Formatter('%(asctime)-15s - [%(threadName)-12.12s]'
                                    ' %(levelname)-8s [%(module)s] - '
                                    '%(message)-s')
        self.logger = logging.getLogger('rbkcli')
        self.logger.status = 'creating'

        self._validate_log_folder(log_name)

        file_handler = RotatingFileHandler(log_name, maxBytes=2000000,
                                           backupCount=5)
        file_handler.setFormatter(formatted)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatted)

        if mode == 'console':
            self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.status = 'created'
        self.status = 'created'


class RbkcliTools():
    '''Define tools to be widely available throughout the code.'''

    def __init__(self, logger, conf_dict={}):
        '''Initialize the tools.'''
        self.logger = logger
        self.ssh_conn = False
        self.called_tools = []
        self.conf_dict = conf_dict
        self.auth = DotDict({})

    def load_yaml_file(self, yaml_file):
        '''Open file as read, load yaml, returns dict.'''
        self.called_tools.append('load_yaml_file')
        
        try: 
            with open(yaml_file, 'r') as file:
                dict_result = yaml.safe_load(file.read())
        except FileNotFoundError as error:
            raise RbkcliException.ToolsError(error)

        return dict_result

    def load_json_file(self, json_file):
        '''Open file as read, load json, returns dict.'''
        self.called_tools.append('load_json_file')
        try:
            with open(json_file, 'r') as file:
                dict_result = json.load(file)
        except FileNotFoundError as error:
            self.safe_create_folder(CONF_FOLDER)
            raise RbkcliException.ToolsError(error)
        except json.decoder.JSONDecodeError as error:
            raise RbkcliException.ToolsError(error)

        return dict_result

    def create_yaml_file(self, yml_dict, yml_file):
        '''Open file as write, dump yaml dict to file.'''
        self.called_tools.append('create_yaml_file')
        try:
            with open(yml_file, 'w') as file:
                yaml.dump(yml_dict, file, default_flow_style=False)
            self.logger.debug('File created successfully: ' + yml_file)

            return True
        except Exception as error:
            msg = 'Execption is ' + error
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(error)

    def create_json_file(self, json_dict, json_file):
        '''Open file as write, dump json dict to file.'''
        self.called_tools.append('create_json_file')
        try:
            with open(json_file, 'w') as file:
                file.write(json.dumps(json_dict, indent=2, sort_keys=True))
            self.logger.debug('IOTools # File created successfully: ' + 
                              json_file)

            return True
        except Exception as error:
            msg = 'Execption is ' + str(error)
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(error)

    def create_simple_swagger_file(self, data, file):
        '''Create a swagger file, version 2, providing minimum data.'''
        self.called_tools.append('create_simple_swagger_file')
        swagger_example = {
            'basePath': data['base_path'],
            'consumes': [
                'application/json'
            ],
            'info': {
                'description': data['description'],
                'title': data['title'],
                'version': '1.0.0'
            },
            'paths': data['paths'],
            'produces': [
                'application/json'
            ],
            'swagger': '2.0'
            }
        return self.create_yaml_file(swagger_example, file)

    def ssh_connection(self, server, username, password, port=22):
        '''Create paramiko's SSH session with provided data.'''
        self.called_tools.append('ssh_connection')
        self.ssh_conn = paramiko.SSHClient()
        self.ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_conn.connect(server,
                              port=port,
                              username=username,
                              password=password)

        return self.ssh_conn

    def ssh_cmd(self, cmd, ssh_conn=''):
        '''Execute ssh command using Paramiko exec_command() method.'''
        self.called_tools.append('ssh_cmd')

        # If connection arg is not given use the instance ssh_con
        if ssh_conn == '':
            ssh_conn = self.ssh_conn

        # Declaring
        results = {}

        stdin, stdout, stderr = ssh_conn.exec_command(cmd)

        # Split session output in a dictionary
        name = ['stdin', 'stdout', 'stderr']
        for item in enumerate([stdin, stdout, stderr]):
            try:
                results[name[item[0]]] = item[1].readlines()
            except IOError:
                results[name[item[0]]] = 'Warning ## cant read content'

        return results

    def ssh_cmd_shell(self, cmd, ssh_conn=''):
        '''Execute ssh command using Paramiko invoke_shell() method.'''
        self.called_tools.append('ssh_cmd_shell')

        # Declaring
        results = []

        ssh_session = ssh_conn.invoke_shell()

        time.sleep(1)
        data = ssh_session.recv(10000)
        for command in cmd:
            ssh_session.send(command + '\n')
            time.sleep(2.5)
            data = ssh_session.recv(10000)
            data = data.decode('utf-8')
            data = data.strip().split('\n')
            results = results + data

        ssh_conn.close()

        return results

    def load_env_auth(self):
        '''Load authentication data from environment variables.'''
        self.called_tools.append('load_env_auth')
        try:
            self.auth.server = os.environ['rubrik_cdm_node_ip']
            self.auth.username = os.environ['rubrik_cdm_username']
            self.auth.password = os.environ['rubrik_cdm_password']
            self.auth.token = os.environ['rubrik_cdm_token']
            
        except KeyError as bad_key:
            if str(bad_key) != "\'rubrik_cdm_token\'":
                msg = '%s%s%s' % ('Unable to load environmental variable for'
                                  ' athentication: ',
                                  bad_key,
                                  '. Are they defined?')
                self.logger.error('IOToolsError # ' + msg)
                raise RbkcliException.ToolsError(msg)
            else:
                # Log successfull actions
                keys = ''
                for line in self.auth.keys():
                    keys = keys + ',' + line
                msg = '%s [%s]' % ('IOTools # Successfully loaded environmental '
                                   'vars', keys.strip(','))
                self.logger.debug(msg)

        return self.auth

    def load_conf_file(self, file='', conf_dict={}):
        '''Load configuration data from json file.'''
        global CONF_DICT
        self.called_tools.append('load_conf_file')

        try:
            if file == '':
                file = CONF_FOLDER + '/rbkcli.conf'
            msg = '%s [%s]' % ('IOTools # Successfully loaded configuration file'
                               ': ', file)
            if conf_dict == {} and self.conf_dict == {}:
                self.conf_dict = self.load_json_file(file)
                self.logger.debug(msg)
            elif isinstance(conf_dict, dict) and self.conf_dict == {}:
                self.conf_dict = conf_dict
                self.logger.debug(msg)
            else:
                msg = 'IOTools # Configuration file already loaded.'
                self.logger.debug(msg)
            CONF_DICT = self.conf_dict
        except RbkcliException.ToolsError as error:
            try:
                self.create_vanila_conf()
                self.load_conf_file()
            except RbkcliException.ToolsError as error:
                msg = 'Unable to load configuration file'
                self.logger.error('IOToolsError # ' + msg)
                raise RbkcliException.ToolsError(msg)
        return self.conf_dict

    def create_vanila_conf(self):
        '''Create a default configuration file.'''
        self.called_tools.append('create_vanila_conf')
        conf_dict = {
            "config": {
                "storeToken": {
                    "value": "False",
                    "description": str("Caches the last successfull token "
                                       "with environment data.")
                },
                "logLevel": {
                    "value": "debug",
                    "description": str("Verbosity of the logs written to the"
                                       " file logs/rbkcli.log.")
                },
                "useCredentialsFile": {
                    "value": "False",
                    "description": str("Tries to load credentials from auth"
                                       " file before looking for env vars.")
                },
                "credentialsFile": {
                    "value": "target.conf",
                    "description": str("File where to load credentials from, "
                                       "before looking for env vars.")
                },
                "whiteList": {
                    "description" : "",
                    "value" : []
                },
                "blackList": {
                    "description" : "",
                    "value" : []
                }
            }
        }
        file = CONF_FOLDER + '/rbkcli.conf'
        try:
            self.safe_create_folder(CONF_FOLDER)
            self.create_json_file(conf_dict, file)
            msg = 'Successfully created new configuration file'
            self.logger.debug('IOTools # ' + msg)
        except:
            msg = 'Unable to create new configuration file'
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(msg)

    def load_auth_file(self):
        '''Load authentication data from json file.'''
        self.called_tools.append('load_auth_file')

        try:
            if self.conf_dict == {}:
                self.load_conf_file()
            file = self.conf_dict['config']['credentialsFile']['value']
            file = CONF_FOLDER + '/' + file
            self.auth_dict = self.load_json_file(file)
        except RbkcliException.ToolsError as error:
            msg = 'Unable to load auth file, [' + file + ']'
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(msg)
 
    def load_file_auth(self):
        '''Load authentication data from json file.'''
        self.called_tools.append('load_file_auth')

        if self.conf_dict['config']['useCredentialsFile']['value'] == 'False':
            msg = 'CredentialsFile is disable, unable to read from file.'
            raise RbkcliException.ToolsError(msg)

        self.load_auth_file()
        auth_keys = ['server', 'token', 'username', 'password']
        for key in auth_keys:
            self.load_auth_key(key)
        # Log successfull actions
        keys = ''
        for line in self.auth.keys():
            keys = keys + ',' + line
        msg = '%s [%s]' % ('IOTools # Successfully loaded file auth data',
                           keys.strip(','))
        self.logger.debug(msg)

        return self.auth

    def load_auth_key(self, key):
        '''Load key by key confirming if consistency is kept.'''
        try:
            self.auth[key] = self.auth_dict[key]

        except KeyError as bad_key:
            if str(bad_key) == "\'token\'":
                if ('username' not in self.auth_dict.keys() and
                  'password' not in self.auth_dict.keys()):
                    msg = '%s%s%s' % ('Unable to load authentication data from'
                                      ' configuration file: ',
                                      bad_key,
                                      '. Are all keys defined correctly?')
                    self.logger.error('IOToolsError # ' + msg)
                    raise RbkcliException.ToolsError(msg)

            elif (str(bad_key) != "\'password\'" or
               str(bad_key) != "\'username\'"):
                msg = '%s%s%s' % ('Unable to load authentication data from '
                                  'configuration file: ',
                                  bad_key,
                                  '. Are all keys defined correctly?')
                self.logger.error('IOToolsError # ' + msg)
                raise RbkcliException.ToolsError(msg)

    def load_auth(self):
        '''Load authentication.'''
        self.called_tools.append('load_auth')
        try:
            self.auth = self.load_file_auth()
        except RbkcliException.ToolsError:
            try:
                self.auth = self.load_env_auth()
            except RbkcliException.ToolsError:
                self.auth = DotDict({})
        
        # Change the verification for target verification, auth verification
        # # To be performed before API execution.
        #if not self._verify_auth_consistency(self.auth):
        #    self.auth = self._load_interactive_auth()
        if not self._verify_target_consistency(self.auth):
            raise Exception('Verify auth code')

        return self.auth

    def _verify_target_consistency(self, auth):
        '''Verify if minimun auth params has been provided.'''        
        self.auth = auth
        if 'server' in self.auth.keys():
            if self.auth.server == '' or not self.is_valid_ip(self.auth.server):
                msg = 'Invalid or missing Rubrik server'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.server = self._user_input('Rubrik server IP: ',
                                                    self.is_valid_ip)
        else:
            msg = 'Invalid or missing authentication parameters.'
            self.logger.error('AuthenticationError # ' + msg)
            self.auth.server = self._user_input('Rubrik server IP: ',
                                                self.is_valid_ip)
        return True

    def _verify_auth_consistency(self, auth):
        '''Verify if minimun auth params has been provided.'''
        self.auth = auth

        ## Fix Clean
        #if 'server' in self.auth.keys():
        #    if self.auth.server == '' or not self.is_valid_ip(self.auth.server):
        #        msg = 'Invalid or missing Rubrik server'
        #        self.logger.error('AuthenticationError # ' + msg)
        #        self.auth.server = self._user_input('Rubrik server IP: ',
        #                                            self.is_valid_ip)
        if 'token' in self.auth.keys():
            if self.auth.token == '' or not self.is_valid_uuid(self.auth.token):
                msg = 'Invalid or missing Rubrik token'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.token = self._user_input('Rubrik API token: ',
                                                    self.is_valid_uuid)
            else:
                pass
                # return True

        if 'username' in self.auth.keys() and 'password' in self.auth.keys():
            if self.auth.username != '' and self.auth.password != '':
                pass
                # return True
            elif self.auth.username == '':
                msg = 'Invalid or missing username/password'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.username = self._user_input('Rubrik username: ',
                                         self.is_not_empty_str)

            elif self.auth.password != '':
                print('password:' + self.auth.password)
                pass
                # return True
            elif self.auth.password == '':
                msg = 'Invalid or missing password format'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.password = self._user_input('Rubrik password: ',
                                         self.is_not_empty_str,
                                         inputer=getpass)
        else:
            msg = 'Invalid or missing authentication parameters.'
            self.logger.error('AuthenticationError # ' + msg)
            return False

        return True

    def _load_interactive_auth(self, auth):
        '''Get auth values from user.'''
        self.auth = auth
        msg = 'Interactive authentication required.'
        self.logger.warning('AuthenticationWarning # ' + msg)
        ## Fix clean
        #self.auth.server = self._user_input('Rubrik server IP: ',
        #                                    self.is_valid_ip)
        self.auth.username = self._user_input('Rubrik username: ',
                                         self.is_not_empty_str)
        self.auth.password = self._user_input('Rubrik password: ',
                                         self.is_not_empty_str,
                                         inputer=getpass)
        if self.conf_dict['config']['useCredentialsFile']['value'] == 'True':
            self._update_auth_file()
        return self.auth

    def _update_auth_file(self):
        '''.'''
        auth_dict = {
            'server': self.auth.server,
            'username': self.auth.username,
            'password': ''
        }
        file = self.conf_dict['config']['credentialsFile']['value']
        file = CONF_FOLDER + '/' + file
        self.create_json_file(auth_dict, file)

    def json_load(self, json_str):
        '''Load json data.'''
        self.called_tools.append('json_dump')

        ##FIX

        try:
            json_dict = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            json_dict = {}

        return json_dict

    def yaml_load(self, yaml_str):
        '''Load yaml data.'''
        self.called_tools.append('json_dump')
        return yaml.safe_load(yaml_str)

    def json_dump(self, json_dict):
        '''Dump json data.'''
        self.called_tools.append('json_dump')

        if not isinstance(json_dict, dict) and not isinstance(json_dict, list):
            json_dict = json.loads(json_dict)

        return json.dumps(json_dict, indent=2, sort_keys=True)

    def jsonfy(self, avar):
        '''.'''
        avar_dict = {}
        if isinstance(avar, requests.models.Response):
            avar_dict = self.json_load(avar.text)
        elif isinstance(avar, dict) or isinstance(avar, list):
            avar_dict = avar
        else:
            avar_dict['result'] = str(avar)

        return self.json_dump(avar_dict)

    def cp_dict(self, existing_dict):
        '''Copy dictionary completly.'''
        self.called_tools.append('cp_dict')
        return copy.deepcopy(existing_dict)

    def download_file(self, url):
        '''Download file from provided url.'''
        self.called_tools.append('download_file')
        pool = urllib3.PoolManager()
        try:
            with pool.request('GET', url, preload_content=False) as file:
                content = file.read()
            if content == b'Route not defined.':
                error = str('Wrong or inexistent URL [' + url + '], route is'
                            ' not defned')
                msg = 'IOToolsError # ' + error
                self.logger.error(msg)
                raise RbkcliException.ToolsError(error)
            else:
                msg = str('IOTools # Successfully downloaded file [%s]' %  url)
                self.logger.debug(msg)
                
        except urllib3.exceptions.MaxRetryError as error:
            msg = 'IOToolsError # ' + str(error)
            self.logger.error(msg)
            raise RbkcliException.ToolsError(str(error))

        return content

    def safe_create_folder(self, folder_path):
        '''Create folders that don't exist in a path provided.'''
        path = ''
        folder_path = folder_path.replace(BASE_FOLDER + "/", "")
        folders = folder_path.strip().split('/')
        try:
            for folder in folders:
                path = path + folder + '/'
                final_path = BASE_FOLDER + "/" + path

                if os.path.isdir(final_path):
                    msg = str('IOTools # Found existing folder [' +
                              final_path + '], not taking action.')
                    self.logger.debug(msg)
                else:
                    os.mkdir(final_path)                    
                    msg = str('IOTools # Could not find folder [' +
                              final_path + '], creating new.')
                    if self.logger.status == 'created':
                        self.logger.warning(msg)
                    else:
                        self.logger.debug(msg)
                final_path = ''
            return True
        except Exception as error:
            self.logger.error('IOToolsError # ' + error)
            return False

    def is_valid_uuid(self, uuid_to_test, version=4):
        '''Copy dictionary completly.'''
        self.called_tools.append('is_valid_uuid')
        try:
            uuid_obj = UUID(uuid_to_test, version=version)
        except:
            return False

        return str(uuid_obj) == uuid_to_test

    def is_valid_ip(self, ip):
        '''Validate if provided IP is valid, takes IPv4/IPv6.'''
        try:
            new_ip = ipaddress.ip_address(ip)
            result = True
        except ValueError:
            result = False

        return result

    def is_not_empty_str(self, value):
        return not value == '' 

    def _user_input(self, msg, validator, inputer=input):
        '''Validate user input.'''
        value = inputer(msg)
        while not validator(value):
            value = input(msg)
        return value


class RbkcliJsonOps():
    '''Manipulates json data in crazy ways.'''
    def __init__(self, logger, json_data=[]):
        '''Initialize the json operation.'''
        self.logger = logger
        self.json_data = json_data
        self._jsonfy()

    def _jsonfy(self):
        '''.'''
        if (not isinstance(self.json_data, dict) and
           not isinstance(self.json_data, list)):
            self.json_data = json.loads(self.json_data)

    def resolve_ref(self, definitions, json_data=[]):
        '''.'''

        # Assign the json data.
        if json_data != [] and json_data != {}:
            self.json_data = json_data

        self.definitions = definitions
        self.json_data = self._iterate_json(self.json_data)

        return self.json_data


    def _iterate_json(self, json_data):
        '''.'''
        new_dict = json_data
        if isinstance(json_data, dict):
            new_dict = self._iterate_dict(json_data)
        elif isinstance(json_data, list):
            new_dict = self._iterate_list(json_data)

        return new_dict

    def _iterate_dict(self, json_data):
        '''.'''
        new_dict = copy.deepcopy(json_data)
        for k,v in json_data.items():
            del new_dict[k]
            k, v = self._action_dict(k, v, json_data)
            new_dict[k] = v
        return new_dict

    def _iterate_list(self, json_data):
        '''.'''
        new_dict = []
        for line in json_data:
            new_dict.append(self._action_list(line, json_data))
        return new_dict

    def _action_dict(self, k, v, json_data):
        '''.'''
        definitions = self.definitions
        new_dict = copy.deepcopy(json_data)
        if k == "$ref":
            keys = self._convert_ref_to_keys(v)
            for nk in keys:
                definitions = definitions[nk]
            k = keys[-1]
            v = self._iterate_json(definitions)
        else:
            v = self._iterate_json(v)
        return k, v

    def _action_list(self, line, json_data):
        '''.'''
        new_dict = self._iterate_json(line)

        return new_dict

    def _convert_ref_to_keys(self, v):
        '''.'''
        keys = v.replace('#', '')
        keys = keys.replace('/definitions/', '')
        if '/' in keys:
            keys = keys.strip().split('/')
        else:
            keys = [keys]

        return keys

    def simple_dict_natural(self, simple_dict={}):
        '''.'''
        if simple_dict == {}:
            simple_dict = self.json_data

        result = []
        for keys, values in simple_dict.items():
            result.append('%s=%s' % (str(keys),str(values)))

        return ','.join(result)

    def natural_simple_dictstr(self, natural_str):
        '''.'''
        simple_dictstr = []

        natural_str = natural_str.split(',')
        for item in natural_str:
            key, value = item.split('=')
            simple_dictstr.append('"%s": "%s"' % (key, value))

        return str('{%s}' % ', '.join(simple_dictstr))
    
    def simple_dict_table(self, simple_dict={}, summary=''):
        '''.'''
        body = {}
        f_body = []
        headers = []
        for key, value in simple_dict[0].items():
            headers.append(key)

        for i in range(0, len(headers)):
            body[i] = []
            for line in simple_dict:
                keyys = list(line.keys())
                body[i].append(line[keyys[i]])
            f_body.append(body[i])

        my_table = DynaTable(headers, f_body, summary=summary,
                         ROW_DIVISION_CHAR="|",
                         LINE_DIVISION_CHAR="=")
        table = my_table.assemble_table()
        return table


class RbkcliBase():
    '''Define the base class for all other classes.'''
    def __init__(self, log_name='empty', module='', user_profile='admin',
                 base_folder='', log_mode=''):
        '''Initialize base class.'''
        self.create_base_folder(base_folder)
        if log_name == 'empty':
            log_name = LOGS_FOLDER + '/rbkcli.log'
        self.user_profile = user_profile
        self.rbkcli_logger = RbkcliLogger(log_name, module, mode=log_mode)
        self.verify_config_keys()

    def json_ops(self, json_data=[]):
        '''Instantiate a new RbkcliJsonOps object.'''
        return RbkcliJsonOps(self.rbkcli_logger, json_data)

    def tools(self):
        '''Instantiate a new set of RbkcliTools object.'''
        return RbkcliTools(self.rbkcli_logger, conf_dict=self.conf_dict)

    def dot_dict(self, dict_={}):
        '''Instantiate a new dot dictionary.'''
        return DotDict(dict_)

    def dyna_table(self, headers, rows, **kwargs):
        '''Instantiate a new dynamic table dictionary.'''
        return DynaTable(headers, rows, logger=self.rbkcli_logger,
                         kwargs=kwargs)

    def api_requester(self, auth):
        '''Instantiate a new API requester.'''
        return ApiRequester(self.rbkcli_logger, self.user_profile, auth=auth)

    def api_handler(self, auth, version):
        '''Instantiate a new API hander.'''
        return RubrikApiHandler(self.rbkcli_logger, auth=auth, version=version,
                                user_profile=self.user_profile)

    def verify_config_keys(self):
        '''.'''
        self.conf_dict = RbkcliTools(self.rbkcli_logger).load_conf_file()
        self.verify_loglevel()

    def verify_loglevel(self):
        '''Upate log level in case config was changed.'''
        new_log_level = self.conf_dict['config']['logLevel']['value']
        if new_log_level == 'error':
            self.rbkcli_logger.logger.setLevel(logging.ERROR)
        elif new_log_level == 'warning':
            self.rbkcli_logger.logger.setLevel(logging.WARNING)

    def create_base_folder(self, base_folder):
        '''.'''
        global BASE_FOLDER
        if base_folder != '':
            BASE_FOLDER = base_folder
        try:
            if not os.path.isdir(BASE_FOLDER):
                os.mkdir(BASE_FOLDER)

        except PermissionError as error:
            print(error)
            exit()
