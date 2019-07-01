"""Cli module for rbkcli."""

import json
import re
import copy

from rbkcli.base import RbkcliException
from rbkcli.base.essentials import DotDict
from rbkcli.core.target import RbkcliTarget


class Rbkcli():
    """Class that provides the connection from any CLI to the Rbkcli."""

    def __init__(self, user_profile='admin', base_folder='', auth=None):
        """Initialize CLI helper."""
        # Instantiate CLI target
        self.ops = []
        self.ops_v = []
        self.args = []
        self.incomplete = ''
        self.result = []
        self.rbk_target = None
        self.ctx = DotDict()
        self.ctx.user_profile = user_profile
        self.ctx.base_folder = base_folder
        self.auth = auth

    def provide_autocomplete(self, ctx, args, incomplete):
        """Provide the autocomplete functionality, with click standard fn.."""
        # Getting list of operations with and without version attached to it.
        self.ctx.workflow = 'complete'
        self.rbk_target = RbkcliTarget(self.ctx, auth=self.auth)
        if self.rbk_target.target.operations == []:
            return []
        self._normalize_ops()
        self.args = args
        self.incomplete = incomplete
        api_vs = self.rbk_target.target.operations.instantiated_api_versions

        # Dividing the workflow between empty args and not empty.
        if args != []:
            if args[0] in api_vs:
                comp = self._selective_autocomplete_without_version(self.ops_v)
            else:
                comp = self._selective_autocomplete_without_version(self.ops)
        else:
            comp = self._full_autocomplete_without_version(self.ops)
        # Return auto complete process.
        del ctx
        return comp

    #def provide_autocomplete_argparse(self, incomplete, args, **ctx):
    def provide_autocomplete_argparse(self, **ctx):
        """Provide the autocomplete functionality, with click standard fn.."""
        # Getting list of operations with and without version attached to it.
        self.ctx.workflow = 'complete'
        self.ctx.parser = ''
        self.rbk_target = RbkcliTarget(self.ctx, auth=self.auth)
        if self.rbk_target.target.operations == []:
            return []
        self._normalize_ops()
        self.args = vars(ctx['parsed_args'])
        self.args = self.args['api_endpoint']
        self.incomplete = ctx['prefix']

        api_vs = self.rbk_target.target.operations.instantiated_api_versions

        # Dividing the workflow between empty args and not empty.
        if self.args is not None:
            if self.args[0] in api_vs:
                comp = self._selective_autocomplete_without_version(self.ops_v)
            else:
                comp = self._selective_autocomplete_without_version(self.ops)
        else:
            comp = self._full_autocomplete_without_version(self.ops)
        # Return auto complete process.
        del ctx
        return comp

    def _normalize_ops(self):
        """Split the operation information to iterate it."""

        for opr in self.rbk_target.target.operations.ops:
            opr = opr.split(':')
            opr_v = opr[0] + '/' + opr[1]
            opr_end = opr[1].split('/')
            opr_end = list(filter(None, opr_end))
            opr_v = opr_v.split('/')
            opr_v = list(filter(None, opr_v))
            self.ops.append(opr_end)
            self.ops_v.append(opr_v)

    def _selective_autocomplete_without_version(self, ops):
        """Iterate available commands based on provided arguments."""
        # Validate endpoint
        returnable_ops = self._get_returnable_ops(ops)

        if returnable_ops != []:

            # Filter ops for valid args
            returnable_ops = self._filter_returnable(returnable_ops)
            comp = self._match_incomplete(returnable_ops)
        else:
            comp = []
        return comp

    def _get_returnable_ops(self, ops):
        """Match available operations based on provided args."""
        new_ops = ops
        flag = ''

        for i in enumerate(self.args):
            ops = new_ops
            new_ops = []
            for opr in ops:
                if i[0] < len(opr) and i[0] < len(self.args):
                    if i[1] == opr[i[0]]:
                        new_ops.append(opr)
                        if i[0] == len(self.args) - 1:
                            flag = 'not_flex'
                    elif re.search('{*id}', opr[i[0]]):
                        if flag != 'not_flex':
                            new_ops.append(opr)

        return new_ops

    def _filter_returnable(self, ops):
        """Filter the operations that are smaller than size of args ."""
        returnable_ops = []
        arg_size = len(self.args)

        for opr in ops:
            if len(opr) - 1 >= arg_size:
                returnable_ops.append(opr[arg_size])

        returnable_ops = list(set(returnable_ops))
        returnable_ops.sort()

        return returnable_ops

    def _match_incomplete(self, ops):
        """Return similar strings, provided a list."""
        ops_return = []
        if self.incomplete != '':
            for line in ops:
                if line.startswith(self.incomplete):
                    ops_return.append(line)
        else:
            ops_return = ops

        return ops_return

    def _full_autocomplete_without_version(self, ops):
        """Iterate only first level of availabel operations ."""

        returnable_ops = []
        ops_return = []

        for opr in ops:
            returnable_ops.append(opr[0])

        returnable_ops = list(set(returnable_ops))
        returnable_ops.sort()

        if self.incomplete != '':
            for line in returnable_ops:
                if line.startswith(self.incomplete):
                    ops_return.append(line)
        else:
            ops_return = returnable_ops

        return ops_return

    def _create_request_structure(self, kwargs, raw_args):
        """Generate the request data structure for target handler."""
        # Define the arguments that will be included in the workflow map.
        workflowable = ['-s', '--select','-f', '--filter', '-c', '--context', '-l', '--loop']
        
        # Create a dictionary that resolved argument to var.
        work_dict = {
            '-s': 'select',
            '--select': 'select',
            '-f': 'filter',
            '--filter': 'filter',
            '-c': 'context',
            '--context': 'context',
            '-l': 'loop',
            '--loop': 'loop'
        }

        # Convert parameters atributes from tuple to list, so its editable.
        ## FIX
        #print('raw_args = ' + str(raw_args))
        new_kwargs = copy.deepcopy(kwargs)
        #print('new_kwargs 1= ' + str(new_kwargs))
        #print(new_kwargs)
        for key, value in kwargs.items():
            new_value = []
            if isinstance(value, tuple):
                for item in value:
                    new_value.append(item)
                new_kwargs[key] = new_value

        #print('new_kwargs 2= ' + str(new_kwargs))
        # Create the workflow dictionary to be passed.
        output_workflow = []
        for arg in raw_args:
            for predicted_arg in workflowable:
                if arg.startswith(predicted_arg):
                    if arg == predicted_arg:
                        value_ = new_kwargs[work_dict[arg]][0]
                        #step = {'arg': work_dict[arg], 'value': value_}
                        if len(value_) > 1:
                            step = {'arg': work_dict[arg], 'value': value_}
                        else:
                            step = {'arg': work_dict[arg], 'value': value_[0]}
                        output_workflow.append(step)
                        # After value has been used remove it from kwargs.
                        new_kwargs[work_dict[arg]].pop(0)
                        # If no other value is available remove key.
                        if new_kwargs[work_dict[arg]] == []:
                            del new_kwargs[work_dict[arg]]
                    else:
                        error = 'The provided argument is invalid [' + arg + ']...'
                        msg = 'RbkcliError # ' + error
                        self.rbk_target.target.rbkcli_logger.error(msg)
                        raise RbkcliException.RbkcliError(error)

        # Add the workflow generated to the parsed arguments.
        #print(new_kwargs)
        new_kwargs['output_workflow'] = output_workflow

        return new_kwargs

    def cli_execute(self, kwargs, raw_args, parser):
        """
        Translate arguments into rbkcli methods.

        The available methods for rbkcli are:
        -execute() # For API requests
        -info() # For summarized info about the provided API
        """
        #print(kwargs)
        self.ctx.workflow = 'command'
        parser.create_request_structure = self._create_request_structure
        self.ctx.parser = parser
        #print('cli_execute:' + str(self.auth))
        self.rbk_target = RbkcliTarget(self.ctx, auth=self.auth)

        ### Testing
        kwargs = self._create_request_structure(kwargs, raw_args)
        #print(kwargs)

        self.result = self.rbk_target.target.command(args=kwargs)

        return self.format_response()

    def format_response(self):
        """
        Format the output of the API command.

        Tests the format of the output and provide it to the click cli,
        accordingly.
        """
        # Try to load as json, if possible create json output.
        try:
            json_dict = json.loads(self.result.text)
            response = json.dumps(json_dict, indent=2)

        except TypeError:
            response = json.dumps(self.result.text, indent=2)

        # If not possible, means output is some other text or empty.
        except json.decoder.JSONDecodeError:

            # If not empty then that text is provided.
            if self.result.text != '':
                response = self.result.text

            # If text is empty provide Response code, for clarity.
            else:
                try:
                    sts_code = self.result.status_code
                except:
                    sts_code = 'EMPTY'
                response = str('Response code: ' +
                               str(sts_code) +
                               '\nResponse text: ' + self.result.text)

        return response

