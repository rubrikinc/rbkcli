"""rbkcli tools module."""

import copy

from getpass import getpass

import ipaddress
import json
import logging

from logging.handlers import RotatingFileHandler

import time
import os
import sys

import uuid
from uuid import UUID

import paramiko
import requests
import urllib3
import yaml

from rbkcli.base.essentials import CONSTANTS, DotDict, RbkcliException


class RbkcliLogger():
    """Customize logger."""
    def __init__(self, log_name, module, mode=''):
        """Initialize logger."""
        self.module = module
        self.logger = logging.getLogger('rbkcli')
        self.logger.status = 'creating'

        self._validate_log_folder(log_name)
        self._configure_logger(log_name, mode)

        self.logger.status = 'created'
        self.status = 'created'

    def error(self, msg):
        """Log an error msg to file."""
        self.logger.error(msg)

    def info(self, msg):
        """Log an info msg to file."""
        self.logger.info(msg)

    def debug(self, msg):
        """Log a debug msg to file.."""
        self.logger.debug(msg)

    def exception(self, msg):
        """Log an exception msg to file.."""
        self.logger.exception(msg)

    def warning(self, msg):
        """Log an warning msg to file.."""
        self.logger.warning(msg)

    def print_error(self, msg):
        """Log and print an error msg to file."""
        print(msg)
        self.logger.error(msg)

    def print_info(self, msg):
        """Log and print an info msg to file."""
        print(msg)
        self.logger.info(msg)

    def print_debug(self, msg):
        """Log and print a debug msg to file.."""
        print(msg)
        self.logger.debug(msg)

    def print_exception(self, msg):
        """Log and print an exception msg to file.."""
        print(msg)
        self.logger.exception(msg)

    def print_warning(self, msg):
        """Log and print an warning msg to file.."""
        print(msg)
        self.logger.warning(msg)

    def _validate_log_folder(self, log_name):
        """Validate the folder provided, if does not exist, create it."""
        try:
            if not os.path.isfile(log_name):
                raise FileNotFoundError(log_name)
        except FileNotFoundError as error:
            folder = log_name.strip().split('/')
            folder.pop(-1)
            folder = '/'.join(folder)
            RbkcliTools(self.logger).safe_create_folder(folder)

    def _configure_logger(self, log_name, mode):
        """Configure logger with console and file handling."""
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
    """Define tools to be widely available throughout the code."""
    def __init__(self, logger, conf_dict={}, workflow='command'):
        """Initialize the tools."""
        self.logger = logger
        self.ssh_conn = False
        self.called_tools = []
        self.conf_dict = conf_dict
        self.workflow = workflow
        self.auth = DotDict({})

    def load_yaml_file(self, yaml_file):
        """Open file as read, load yaml, returns dict."""
        self.called_tools.append('load_yaml_file')
        
        try: 
            with open(yaml_file, 'r') as file:
                dict_result = yaml.safe_load(file.read())
        except FileNotFoundError as error:
            raise RbkcliException.ToolsError(error)

        return dict_result

    def load_json_file(self, json_file):
        """Open file as read, load json, returns dict."""
        self.called_tools.append('load_json_file')
        try:
            with open(json_file, 'r') as file:
                dict_result = json.load(file)
        except FileNotFoundError as error:
            self.safe_create_folder(CONSTANTS.CONF_FOLDER)
            raise RbkcliException.ToolsError(error)
        except json.decoder.JSONDecodeError as error:
            raise RbkcliException.ToolsError(error)

        return dict_result

    def create_yaml_file(self, yml_dict, yml_file):
        """Open file as write, dump yaml dict to file."""
        self.called_tools.append('create_yaml_file')
        try:
            with open(yml_file, 'w') as file:
                yaml.dump(yml_dict, file, default_flow_style=False)
            self.logger.debug('File created successfully: ' + yml_file)

            return True
        except FileNotFoundError as error:
            error = str(error) + '\n'
            msg = 'Execption is ' + error
            self.logger.error('IOToolsError # ' + msg)
            return False

        except Exception as error:
            error = str(error) + '\n'
            msg = 'Execption is ' + error
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(error)

    def create_json_file(self, json_dict, json_file):
        """Open file as write, dump json dict to file."""
        self.called_tools.append('create_json_file')
        try:
            with open(json_file, 'w') as file:
                file.write(json.dumps(json_dict, indent=2, sort_keys=True))
            self.logger.debug('IOTools # File created successfully: ' + 
                              json_file)
            return True
        except FileNotFoundError as error:
            error = str(error) + '\n'
            msg = 'Execption is ' + error
            self.logger.error('IOToolsError # ' + msg)
            return False

        except Exception as error:
            error = str(error) + '\n'
            msg = 'Execption is ' + str(error)
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(error)
        return False

    def safe_create_json_file(self, json_dict, json_file):
        """Open file as write, dump json dict to file."""
        if os.path.isfile(json_file):
            return False
        else:
            if not self.create_json_file(json_dict, json_file):
                return False
        return True

    def create_simple_swagger_file(self, data, file):
        """Create a swagger file, version 2, providing minimum data."""
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
        """Create paramiko's SSH session with provided data."""
        self.called_tools.append('ssh_connection')
        self.ssh_conn = paramiko.SSHClient()
        self.ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_conn.connect(server,
                              port=port,
                              username=username,
                              password=password)

        return self.ssh_conn

    def ssh_cmd(self, cmd, ssh_conn=''):
        """Execute ssh command using Paramiko exec_command() method."""
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
        """Execute ssh command using Paramiko invoke_shell() method."""
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
        """Load authentication data from environment variables."""
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
                msg = '%s [%s]' % ('IOTools # Successfully loaded'
                                   ' environmental vars', keys.strip(','))
                self.logger.debug(msg)

        return self.auth

    def load_conf_file(self, file='', conf_dict={}):
        """Load configuration data from json file."""
        self.called_tools.append('load_conf_file')

        try:
            if file == '':
                file = CONSTANTS.CONF_FOLDER + '/rbkcli.conf'
            msg = '%s [%s]' % ('IOTools # Successfully loaded configuration'
                               ' file: ', file)
            if conf_dict == {} and self.conf_dict == {}:
                self.conf_dict = self.load_json_file(file)
                self.logger.debug(msg)
            elif isinstance(conf_dict, dict) and self.conf_dict == {}:
                self.conf_dict = conf_dict
                self.logger.debug(msg)
            else:
                msg = 'IOTools # Configuration file already loaded.'
                self.logger.debug(msg)
            CONSTANTS.CONF_DICT = self.conf_dict
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
        """Create a default configuration file."""
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
                    "value" : [
                                'rbkcli:/cmdlet/profile:get:NA',
                                'rbkcli:/cmdlet/profile:post:NA',
                                'rbkcli:/cmdlet/sync:post:NA',
                                'rbkcli:/cmdlet:delete:NA',
                                'rbkcli:/cmdlet:get:NA',
                                'rbkcli:/cmdlet:post:NA',
                                'rbkcli:/commands:get:NA',
                                'rbkcli:/jsonfy:get:NA',
                                'rbkcli:/script/sync:post:NA',
                                'rbkcli:/script:get:NA'
                            ]
                },
                "blackList": {
                    "description" : "",
                    "value" : []
                }
            }
        }
        file = CONSTANTS.CONF_FOLDER + '/rbkcli.conf'
        try:
            self.safe_create_folder(CONSTANTS.CONF_FOLDER)
            self.create_json_file(conf_dict, file)
            msg = 'Successfully created new configuration file'
            self.logger.debug('IOTools # ' + msg)
        except:
            msg = 'Unable to create new configuration file'
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(msg)

    def load_auth_file(self):
        """Load authentication data from json file."""
        self.called_tools.append('load_auth_file')

        try:
            if self.conf_dict == {}:
                self.load_conf_file()
            file = self.conf_dict['config']['credentialsFile']['value']
            file = CONSTANTS.CONF_FOLDER + '/' + file
            self.auth_dict = self.load_json_file(file)
        except RbkcliException.ToolsError as error:
            msg = 'Unable to load auth file, [' + file + ']'
            self.logger.error('IOToolsError # ' + msg)
            raise RbkcliException.ToolsError(msg)
 
    def load_file_auth(self):
        """Load authentication data from json file."""
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
        """Load key by key confirming if consistency is kept."""
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
        """Load authentication."""
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
        if not self._verify_target_consistency(self.auth):
            raise Exception('Verify auth code')

        return self.auth

    def _verify_target_consistency(self, auth):
        """Verify if minimun auth params has been provided."""   
        self.auth = auth
        if 'server' in self.auth.keys():
            if (self.auth.server == '' or
                not self.is_valid_ip_port(self.auth.server)):
                if self.workflow == 'command':
                    msg = 'Invalid or missing Rubrik server'
                    self.logger.error('AuthenticationError # ' + msg)
                    self.auth.server = self._user_input('Rubrik server IP: ',
                                                        self.is_valid_ip_port)
        else:
            if self.workflow == 'command':
                msg = 'Invalid or missing authentication parameters.'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.server = self._user_input('Rubrik server IP: ',
                                                    self.is_valid_ip_port)
            elif self.workflow == 'complete':
                self.auth.server = ''
        return True

    def verify_auth_consistency(self, auth):
        """Verify if minimun auth params has been provided."""
        self.auth = auth

        ## Fix Clean
        if 'token' in self.auth.keys():
            if self.auth.token == '' or not self.is_valid_uuid(self.auth.token):
                msg = 'Invalid or missing Rubrik token'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.token = self._user_input('Rubrik API token: ',
                                                    self.is_valid_uuid)
            else:
                pass

        if 'username' in self.auth.keys() and 'password' in self.auth.keys():
            if self.auth.username != '' and self.auth.password != '':
                pass
            elif self.auth.username == '':
                msg = 'Invalid or missing username/password'
                self.logger.error('AuthenticationError # ' + msg)
                self.auth.username = self._user_input('Rubrik username: ',
                                         self.is_not_empty_str)
            elif self.auth.password != '':
                print('password:' + self.auth.password)
                pass
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

    def load_interactive_auth(self, auth):
        """Get auth values from user."""
        self.auth = auth
        msg = 'Interactive authentication required.'
        self.logger.warning('AuthenticationWarning # ' + msg)
        ## Fix clean
        self.auth.username = self._user_input('Rubrik username: ',
                                         self.is_not_empty_str)
        self.auth.password = self._user_input('Rubrik password: ',
                                         self.is_not_empty_str,
                                         inputer=getpass)
        if self.conf_dict['config']['useCredentialsFile']['value'] == 'True':
            self._update_auth_file()
        return self.auth

    def _update_auth_file(self):
        """Add server and username to auth file."""
        auth_dict = {
            'server': self.auth.server,
            'username': self.auth.username,
            'password': ''
        }
        file = self.conf_dict['config']['credentialsFile']['value']
        file = CONSTANTS.CONF_FOLDER + '/' + file
        self.create_json_file(auth_dict, file)

    def json_load(self, json_str):
        """Load json data."""
        self.called_tools.append('json_dump')

        ##FIX
        try:
            json_dict = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            json_dict = {}

        return json_dict

    def yaml_load(self, yaml_str):
        """Load yaml data."""
        self.called_tools.append('json_dump')
        return yaml.safe_load(yaml_str)

    def json_dump(self, json_dict):
        """Dump json data."""
        self.called_tools.append('json_dump')

        if not isinstance(json_dict, dict) and not isinstance(json_dict, list):
            json_dict = json.loads(json_dict)

        return json.dumps(json_dict, indent=2, sort_keys=True)

    def jsonfy(self, avar):
        """Load json data from string."""
        avar_dict = {}
        if isinstance(avar, requests.models.Response):
            avar_dict = self.json_load(avar.text)
        elif isinstance(avar, dict) or isinstance(avar, list):
            avar_dict = avar
        else:
            avar_dict['result'] = str(avar)

        return self.json_dump(avar_dict)

    def cp_dict(self, existing_dict):
        """Copy dictionary completly."""
        self.called_tools.append('cp_dict')
        return copy.deepcopy(existing_dict)

    def download_file(self, url):
        """Download file from provided url."""
        self.called_tools.append('download_file')
        pool = urllib3.PoolManager(cert_reqs='CERT_NONE')
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
        """Create folders that don't exist in a path provided."""
        path = ''
        folder_path = folder_path.replace(CONSTANTS.BASE_FOLDER + "/", "")
        folders = folder_path.strip().split('/')
        try:
            for folder in folders:
                path = path + folder + '/'
                final_path = CONSTANTS.BASE_FOLDER + "/" + path

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

    def is_valid_uuid1(self, uuid_to_test, version=4):
        """Copy dictionary completly."""
        self.called_tools.append('is_valid_uuid')
        try:
            uuid_obj = UUID(uuid_to_test, version=version)
        except:
            return False

        return str(uuid_obj) == uuid_to_test

    def is_valid_uuid(self, uuid_to_test, version=4):
        """Copy dictionary completly."""
        # Because of the creation of the universal ID rbkcli no longer
        # verifies id validity
        self.called_tools.append('is_valid_uuid')

        return True

    def is_valid_ip(self, ip):
        """Validate if provided IP is valid, takes IPv4/IPv6."""
        try:
            new_ip = ipaddress.ip_address(ip)
            result = True
        except ValueError:
            result = False

        return result

    def is_valid_ip_port(self, ip_port):
        """Validate if provided IP is valid, takes IPv4/IPv6."""
        if ':' in ip_port:
            ip, port = ip_port.split(':')
            try:
                if (self.is_valid_ip(ip) and
                    int(port) < 65535 and int(port) > 0):
                    return True
                else:
                    return False
            except ValueError:
                return False
        else:
            return self.is_valid_ip(ip_port)

    def is_not_empty_str(self, value):
        """Test if string is not empty."""
        return not value == '' 

    def _user_input(self, msg, validator, inputer=input):
        """Validate user input."""
        value = inputer(msg)
        while not validator(value):
            value = input(msg)
        return value

    def gen_uuid(self):
        """Generate UUID version 4."""
        return uuid.uuid4()