"""Analyze API metrics from spray-server logs."""

import gzip
import json
import os

from rbkcli import RbkCliBlackOps, RbkcliException


class LogApiMetric(RbkCliBlackOps):
    """
    Define the operation in rbkcli framework.

    Description:
    -Provide the structure of the endpoint being created  by this script,
     as if a RestFUL API endpoint, do it so by filling in the minimum
     necessary properties.

    Properties:
    -method = [string] The method by which this endpoint will be evoked
    -endpoint = [string] The /path/command_line to call this script
    -description = [string] A explanation of the main features of the script
    -summary = [string] A summarize explanation of the script
    -parameters = [list] of [dictionary] define the parameters  which are
    expected and used in the script.
    [
        {
            'name': '<parameter_name>',
            'description': 'Description of the parameter.',
            'in': 'Where to provide the parameter, could be [body, path]',
            'required': True/False (if its required to run the script),
            'type': 'data type of parameter
        }
    ]
    """
    method = 'get'
    endpoint = '/log/api_metric'
    description = str('Parse spray-server logs for API Metrics.')
    summary = 'Parse provided spray-server logs isolating API Metrics.'
    parameters = [
        {
            'name': 'limit',
            'description': str('Amount of results parsed per node folder, '
                               'default is 100.'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'folder',
            'description': str('Folder path from where the logs will be '
                               'parsed, default is current working directory'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'user_id_line_tolerance',
            'description': str('How far back on the thread lines from the '
                               'logs, the script will search for a user '
                               'authentication. Default is 300 lines.'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'max_dur',
            'description': str('Maximum API metric duration, discards '
                               'anything over this value.'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'min_dur',
            'description': str('Minimum API metric duration, discards '
                               'anything under this value.'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'duration',
            'description': str('Search for the API metrics with the exact'
                               ' duration provided'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'path',
            'description': str('API endpoint path, only return results for '
                               'the provided path.'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'method',
            'description': 'API endpoint method (GET, POST, PATCH...).',
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'apiVersion',
            'description': 'API endpoint version (v1, v2 and internal)',
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'referer',
            'description': str('Type of API client initiated the API call, '
                               'could be webapp, python...'),
            'in': 'body',
            'required': False,
            'type': 'string'
        }
    ]

    def execute(self, args):
        """
        Method that calls operation from rbkcli framework.

        Description:
        -It will pass the variable args with the following structure:
        {
            'endpoint': 'path/command_line',
            'parameters': {
                '<parameter_name>': '<parameter_value>'
                },
            'method': 'get',
            'target': 'rbkcli target server',
            'query': '<query string passed>'
        }
        Once the variable args is a  DotDictionary its elements can be
        accessed as a property would be.
        Example:
            print(args.parameters.parameter_name)
        """
        api_metric = ApiMetric(self.rbkcli, self.parameters)
        return api_metric.metricfy(args)


class ApiMetric:
    """Class to perform the log parsing."""
    def __init__(self, rbkcli, parameters):
        # Define the search parameters for the logs.
        self.PARSE_SELECT = 'API METRIC {'
        self.search = {}
        self.threads = {}
        self.users = []
        self.counter = 0
        self.rbkcli = rbkcli
        self.parameters = parameters

    def metricfy(self, args):
        """Generate metric results from API logs."""
        self._assign_defined_param(args)
        self.search = args.parameters

        # Get all nodes.
        nodes = self.rbkcli.call_back('cluster me node -s id')
        nodes_id = json.loads(nodes.text)

        # Get all users.
        users = self.rbkcli.call_back('user')
        self.users = json.loads(users.text)

        # Declare vars
        result = []
        # log_location = ''
        log_folders = self.get_folder_path()

        # Loop through the nodes of the cluster.
        for node in nodes_id:

            log_files = self.get_log_files(node['id'], log_folders)

            self.counter = 0
            for file in log_files:
                if self.counter >= self.limit:
                    break
                result = result + self.analyze_metric_logs(file, node)

        return result

    def _assign_defined_param(self, args):
        """Load all defined parameters with the provided value."""
        args.param = {}
        for param in self.parameters:
            name = param['name']
            try:
                args.param[name] = args.parameters[name]
            except KeyError:
                if param['required']:
                    raise RbkcliException.ScriptError('The parameter %s is '
                                                      'required.' % name)
                args.param[name] = None

        # If no limit was set, set default to 100.
        if args.param['limit'] is None:
            self.limit = 100
        else:
            self.limit = int(args.param['limit'])

        # If no limit was set, set default to 300.
        if args.param['user_id_line_tolerance'] is None:
            self.line_tlrnc = 300
        else:
            self.line_tlrnc = int(args.param['user_id_line_tolerance'])

        # If no limit was set, set default to local working dir.
        if args.param['folder'] is None:
            self.source_folder = os.getcwd()
        else:
            self.source_folder = args.param['folder']

        return args

    def get_folder_path(self):
        """Get child folder from provided location with spray logs."""
        log_folders = []
        for root, dirs, files in os.walk(self.source_folder):
            if '/spray-server' in str(root) and 'current' in files:
                log_folders.append([root, files])
        return log_folders

    @staticmethod
    def get_log_files(node, log_folders):
        """Get independent log file paths."""
        log_files = []

        for folder, files in log_folders:
            if node in folder:
                for file in files:
                    if file != 'state':
                        log_files.append(folder + '/' + file)

        return log_files

    def analyze_metric_logs(self, log_path, node):
        """Load the log file found and start metric analysis."""

        # Declare all needed variables.
        final_metric = []

        # Load log file
        try:
            if '.s' in log_path:
                with gzip.open(log_path, 'r') as f:
                    current_log = f.readlines()
            elif 'current' in log_path:
                with open(log_path, 'r') as f:
                    current_log = f.readlines()
            else:
                return []
        except FileNotFoundError as error:
            print('No logs found for the following node: %s \n %s'
                  % (node['id'], error))
            return []
        except Exception as error:
            print('Unexpected error while parsing node: %s \n %s'
                  % (node['id'], error))
            return []

        api_events = self.gen_api_obj(current_log, node, log_path)

        for metric in api_events:
            final_metric.append(self.build_metric_obj(metric, current_log))

        return final_metric

    def build_metric_obj(self, metric, current_log):
        """Create the metric object by extracting useful data."""

        relevant_data = self.get_relevant_lines(metric, current_log)
        metric, important_line = self.refine_relevant_lines(metric,
                                                            relevant_data)

        user_line, metric = self.extract_userline(important_line, metric)

        metric['user'], metric['user_id'] = self.resolve_user(user_line,
                                                              metric['thread'])
        metric['thread'] = self.sort_threads(metric['thread'], metric['logs'])

        return metric

    @staticmethod
    def extract_userline(important_line, metric):
        """Extract log lines which match the provided string."""

        user_line = []

        # This is where all other information is taken.
        auth_line_1 = str('impl.HierarchyBasedAuthorizationContextFor'
                          'Principal')
        auth_line_2 = str('[impl.RequestContextFactoryImpl]  Checking'
                          ' principal:')
        for line in enumerate(important_line):
            if auth_line_1 in line[1] or auth_line_2 in line[1]:
                user_line.append(line[1])
                if line[1] not in metric['logs']:
                    metric['logs'].append(line[1])

        return user_line, metric

    def resolve_user(self, user_line, thread):
        """Convert user id found into username."""
        if len(user_line) > 1:
            return self.parse_principal(user_line[-1], thread)
        elif len(user_line) == 0:
            return self.parse_principal('', thread)
        else:
            return self.parse_principal(user_line[0], thread)

    @staticmethod
    def get_relevant_lines(metric, current_log):
        """Get all lines with the same thread for the log found."""
        # Declare all needed variables.
        thread_lines = []
        prev_thread_lines = []

        metric_thread = metric['thread'].strip('<').strip('>').split('-')
        prev_thread = metric_thread[:-1]
        prev_thread.append(str(int(metric_thread[-1]) - 1))
        prev_thread = str('<' + '-'.join(prev_thread) + '>')

        for line in enumerate(current_log):
            log_line = line[1]
            if isinstance(log_line, bytes):
                log_line = log_line.decode("utf-8")
            if metric['thread'] in log_line:
                thread_lines.append(log_line)
            elif prev_thread in log_line:
                prev_thread_lines.append(log_line)

        relevant_data = {
            'thread_lines': thread_lines,
            'prev_thread_lines': prev_thread_lines,
            'metric_thread': metric_thread,
            'prev_thread': prev_thread
        }

        return relevant_data

    def refine_relevant_lines(self, metric, relevant_data):
        """Apply line tolerance to the important lines."""
        important_line = []

        l_t = self.line_tlrnc
        for line in enumerate(relevant_data['thread_lines']):
            i = line[0]
            l_t = self.line_tlrnc
            if l_t > i:
                l_t = i

            if metric['logs'][0] == line[1]:
                important_line = relevant_data['thread_lines'][i - l_t:i]

        if len(relevant_data['prev_thread_lines']) > 0:
            all_thread = [metric['thread'], relevant_data['prev_thread']]
            metric['thread'] = all_thread
            limited_lines = relevant_data['prev_thread_lines'][-l_t:]
            important_line = important_line + limited_lines
        else:
            metric['thread'] = [metric['thread']]

        return metric, important_line

    def gen_api_obj(self, current_log, node, log_path):
        """Get API Metric event."""

        # Declare all needed variables.
        api_events = []

        for line in enumerate(current_log):
            log_line = line[1]
            if isinstance(log_line, bytes):
                log_line = log_line.decode("utf-8")
            if self.PARSE_SELECT in log_line:
                log_event = self.parse_log_line(log_line)

                api_metric = log_event['message'].split()
                try:
                    log_event['api_metric'] = json.loads(api_metric[2])
                except json.decoder.JSONDecodeError:
                    not_loadable = {'not_loadable': str(api_metric[2])}
                    log_event['api_metric'] = not_loadable

                del log_event['message']

                log_event['node'] = node['id']
                log_event['log_file'] = log_path

                if self.is_desired_result(log_event):
                    api_events.append(log_event)
                    self.counter += 1
            if self.counter >= self.limit:
                break

        return api_events

    def is_desired_result(self, log_event):
        """Filter desired result from log line."""
        desired = True
        for key, value in log_event['api_metric'].items():
            if key in self.search.keys():
                if self.search[key] in str(value):
                    desired = True
                else:
                    return False
            if 'min_dur' in self.search.keys():
                if key == 'duration':
                    if int(value) > int(self.search['min_dur']):
                        desired = True
                    else:
                        return False
            if 'max_dur' in self.search.keys():
                if key == 'duration':
                    if int(value) < int(self.search['max_dur']):
                        desired = True
                    else:
                        return False
            if self.search == {}:
                return True

        return desired

    def parse_principal(self, log_line, thread):
        """Parse user if from log line."""
        user = log_line.split()
        if 'Checking principal:' in log_line:
            user_id = str('User:::' + user[-1])
            self.threads[user[2]] = user_id
        elif 'ContextForPrincipal' in log_line:
            user_id = user[-3]
            self.threads[user[2]] = user_id
        else:
            user_id = 'NO_USER_FOUND_IN_LOGS'
            for thrd_nb in thread:
                if thrd_nb in list(self.threads.keys()):
                    user_id = self.threads[thrd_nb]

        for a_user in self.users:
            if user_id == a_user['id']:
                return a_user['username'], user_id

        return user_id, user_id

    @staticmethod
    def parse_log_line(str_line):
        """Create a json object from log line."""
        log_line = str_line.split()

        log_event = {
            'date': log_line[0],
            'verbosity': log_line[1],
            'thread': log_line[2],
            'module': log_line[3],
            'message': ' '.join(log_line[4:]),
            'logs': [str_line]
        }

        return log_event

    @staticmethod
    def sort_threads(threads, logs):
        """Create list of threads related to the API metric."""
        final_threads = []
        for thread in threads:
            for log in logs:
                if thread in log:
                    final_threads.append(thread)

        return sorted(list(set(final_threads)))
