"""Command Line Interface module with autocomplete."""
from __future__ import print_function

import sys
import argparse
import argcomplete

from rbkcli.base.essentials import RbkcliException
from rbkcli.interface.cli import Rbkcli


# Instantiating the target for the CLI as global var.
try:
    RBK = Rbkcli()
except RbkcliException.ApiRequesterError as error:
    print('ImportApis # ' + str(error))
    exit()
except KeyboardInterrupt:
    print('\nUserError # Operation Aborted!\n')
    exit()


class CustomizedHelpFormatter(argparse.HelpFormatter):
    """
    DESCRIPTION: Formatter class child of argparser's HelpFormatter, where
    we change the prefix of the usage message.
    """

    def add_usage(self, usage, actions, groups, prefix=None):
        """
        DESCRIPTION: Changes the prefix of usage to a custom version.
        """
        if prefix is None:
            prefix = '==> Here\'s some help <==: '

        return super(CustomizedHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)


class CustomParser(argparse.ArgumentParser):
    """
    DESCRIPTION: Child class from ArgumentParser, used to customize the error
    message.
    """

    def error(self, message):
        """
        DESCRIPTION: Function which overrides the original error from argparse
        """

        # Changed the prefix of message to be printed and the order.
        def print_error_usage(message):
            error_msg = str(('ArgumentError # %s\n\nUsage:') % (message) +
                            self.usage)
            sys.stderr.write(error_msg)
            sys.exit(2)

        self.exit(print_error_usage(message))

    def general_error(self, message):
        """
        DESCRIPTION: Function which overrides the original error from argparse
        """

        # Changed the prefix of message to be printed and the order.
        def print_error_usage(message):
            sys.stderr.write(message)
            sys.exit(2)

        self.exit(print_error_usage(message))


class RbkCli():
    def __init__(self, auth=None):
        # Definninf the CLI.
        global RBK
        self.operation = self._define_cli()
        self.auth = auth
        if auth is not None:
            RBK = Rbkcli(auth=self.auth)

    def execute(self, arg_list):
        # Parsing the CLI.
        self.arg_list = arg_list

        if isinstance(self.arg_list, str):
            self.arg_list = self.arg_list.split()

        self.args = self.operation.parse_args(self.arg_list)

        # Getting results to a dictionary
        self.args_dict = vars(self.args)
        self.args_dict = self._un_list(self.args_dict)
        self.operation.un_list = self._un_list

        self._auth_parameters()
        try:
            return self._execute(self.args_dict, self.arg_list, self.operation)
        except RbkcliException as msg:
            self.operation.general_error(str(msg))

    def _auth_parameters(self, ):
        global RBK
        if self.args_dict['credentials'] is not None:
            creds = self.args_dict['credentials'][0][0].split(':')
            if len(creds) == 3:
                self.auth = {
                    'server': creds[0],
                    'username': creds[1], 
                    'password': creds[2]
                }
            elif len(creds) == 4:
                self.auth = {
                    'server': '%s:%s' % (creds[0], creds[1]),
                    'username': creds[2], 
                    'password': creds[3]
                }
            else:
                raise self.operation.error('CLI # Wrong Credentials parameter provided. '
                                           'Please provide <node_ip>:<port>:<username>:<password>')
                exit()
            RBK = Rbkcli(auth=self.auth)

    def _define_cli(self):
        prog = 'rbkcli'
        description = 'Easy calls to Rubrik APIs from CLI.'

        # Making sure description will always have the prog name prior to
        # description, the prog, might be passed as by dynaSwitch
        description = '> [' + prog + '] ' + description

        epilog = str('For all available commands run: '
                     '$ rbkcli commands -q <cmd_name>')

        # Creating custom usage msg, based on new attributes "Instructions"
        # and "Example".
        usage = str('\n  $ rbkcli <api_endpoint> <options>'
                    '\n  $ rbkcli cluster me --select id\n')

        operation = CustomParser(prog=prog,
                                 description=description,
                                 usage=usage,
                                 epilog=epilog)

        # Changing hidden title attributes to a custom value.
        operation._positionals.title = '==> Positional arguments <=='
        operation._optionals.title = '==> Optional arguments <=='

        # The API endpoint to be requested, required argument.
        help_msg = 'The API endpoint to be requested, required argument'
        arg_cmplt = RBK.provide_autocomplete_argparse
        operation.add_argument('api_endpoint',
                               metavar=('<api_endpoint>'),
                               type=str,
                               nargs='+',
                               help=help_msg).completer = arg_cmplt
                               
        # Defining the optional arguments for backup
        # The method to reach the endpoint, default is get.
        help_msg = 'Method to request Rubrik API'
        operation.add_argument('-m',
                               '--method',
                               metavar=('<method>'),
                               type=str,
                               nargs=1,
                               help=help_msg,
                               default='get')

        # Version of the imported API in the target.
        help_msg = 'Explicit version of the Endpoint requested.'
        operation.add_argument('-v',
                               '--version',
                               metavar=('<version>'),
                               type=str,
                               nargs=1,
                               help=help_msg,
                               default='')

        # In path query to customize API request.
        help_msg = 'In path query to customize API request.'
        operation.add_argument('-q',
                               '--query',
                               metavar=('<query>'),
                               type=str,
                               nargs=1,
                               help=help_msg,
                               default='')

        # Parameter passed to the API request, json.
        help_msg = 'Parameter passed to the API request, json.'
        operation.add_argument('-p',
                               '--parameter',
                               metavar=('<parameter>'),
                               type=str,
                               nargs=1,
                               help=help_msg,
                               default={})

        # Flag to return information on the Provided API endpoint.
        help_msg = 'Flag to return information on the Provided API endpoint.'
        operation.add_argument('-i',
                               '--info',
                               action='store_true',
                               help=help_msg)

        # Documentation related to the provided endpoint and method.
        help_msg = 'Documentation related to the provided endpoint and method.'
        operation.add_argument('-d',
                               '--documentation',
                               action='store_true',
                               help=help_msg)

        # Select the json fields from the output.
        help_msg = 'Select the json fields from the output.'
        operation.add_argument('-s',
                               '--select',
                               metavar=('<select>'),
                               action='append',
                               type=str,
                               nargs=1,
                               help=help_msg)

        # Filter the value of the provided fields from the json results.
        help_msg = str('Filter the value of the provided fields from the json'
                       ' results.')
        operation.add_argument('-f',
                               '--filter',
                               metavar=('<filter>'),
                               action='append',
                               type=str,
                               nargs=1,
                               help=help_msg)

        # Cut the json output into the provided field of context.
        help_msg = 'Cut the json output into the provided field of context.'
        operation.add_argument('-c',
                               '--context',
                               metavar=('<context>'),
                               action='append',
                               type=str,
                               nargs=1,
                               help=help_msg)

        # Loop resulting json values into another API request.
        help_msg = 'Loop resulting json values into another API request.'
        operation.add_argument('-l',
                               '--loop',
                               metavar=('<key>', '<new_endpoint>'),
                               action='append',
                               type=str,
                               nargs=2,
                               help=help_msg)

        # Loop resulting json values into another API request.
        help_msg = 'Pass credentials as arguments to run the agains.'
        operation.add_argument('-C',
                               '--credentials',
                               metavar=('<node_ip>:<port>:<username>:<password>'),
                               action='append',
                               type=str,
                               nargs=1,
                               help=help_msg)
        
        out_format = operation.add_mutually_exclusive_group(required=False)
        # Convert json output into Table output, if possible.
        help_msg = 'Convert json output into Table output, if possible.'
        out_format.add_argument('-T',
                               '--table',
                               action='store_true',
                               help=help_msg)

        # Convert json output into Table output, if possible.
        help_msg = 'Convert json output into list output, if possible.'
        out_format.add_argument('-L',
                               '--list',
                               action='store_true',
                               help=help_msg)

        # Convert json output into Table output, if possible.
        help_msg = 'Convert json output into list output, if possible.'
        out_format.add_argument('-P',
                               '--pretty_print',
                               action='store_true',
                               help=help_msg)
        # Convert json output into html table output, if possible.
        help_msg = 'Convert json output into html table output, if possible.'
        out_format.add_argument('-H',
                               '--html',
                               action='store_true',
                               help=help_msg)

        argcomplete.autocomplete(operation)

        return operation

    def _un_list(self, args_dict):
        un_listable = ['version', 'method', 'parameter', 'query']
        for key, value in args_dict.items():
            if key in un_listable and isinstance(value, list):
                value = value[0]
                args_dict[key] = value
        return args_dict

    def _execute(self, args_dict, arg_list, operation):
        try:
            return RBK.cli_execute(args_dict, arg_list, operation)
        except RbkcliException.ApiRequesterError as error:
            raise RbkcliException('ApiRequester # ' + str(error))
        except RbkcliException.DynaTableError as error:
            raise RbkcliException('DynamicTable # ' + str(error))
        except RbkcliException.ToolsError as error:
            raise RbkcliException('IOTools # ' + str(error))
        except RbkcliException.LoggerError as error:
            raise RbkcliException('Logger # ' + str(error))
        except RbkcliException.ClusterError as error:
            raise RbkcliException('ApiTarget # ' + str(error))
        except RbkcliException.ApiHandlerError as error:
            raise RbkcliException('ApiHandler # ' + str(error))
        except RbkcliException.ScriptError as error:
            raise RbkcliException('Scripts # ' + str(error))
        except RbkcliException.RbkcliError as error:
            operation.error(str(error))
        except KeyboardInterrupt:
            raise RbkcliException('\nUserError # Operation Aborted!\n')


def main():
    """Gather args and call cli function."""
    # Getting provided arguments
    arg_list = sys.argv[1:]
    rbk_cli = RbkCli()
    print(rbk_cli.execute(arg_list))

if __name__ == '__main__':
    # If cli file is executed directly, will call main.
    main()
