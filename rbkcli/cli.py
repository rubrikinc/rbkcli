'''Cli module for rbkcli'''

import json
import re
from rbkcli.target import RbkcliTarget


class Rbkcli():
    '''Class that provides the connection from any CLI to the Rbkcli.'''

    def __init__(self, user_profile='admin'):
        '''Initialize CLI helper.'''

        # Instantiate CLI target
        self.rbk_target = RbkcliTarget(user_profile=user_profile)

    def provide_autocomplete(self, ctx, args, incomplete):
        '''Provide the autocomplete functionality, with click standard fn..'''
        ops, ops_v = self._normalize_ops()
        if args != []:
            if args[0] in self.rbk_target.target.operations.instantiated_api_versions:
                comp = self._selective_autocomplete_without_version(ops_v,
                                                                    args,
                                                                    incomplete)
            else:
                comp = self._selective_autocomplete_without_version(ops,
                                                                    args,
                                                                    incomplete)
        else:
            comp = self._full_autocomplete_without_version(ops,
                                                           args,
                                                           incomplete)
        return comp

    def _normalize_ops(self):
        '''Split the operation information to iterate it.'''
        ops = []
        ops_v = []
        for op in self.rbk_target.target.operations.ops:
            op_v, op_end, op_meth, op_com = op.split(':')
            op_v = op_v + '/' + op_end
            op_end = op_end.split('/')
            op_end = list(filter(None, op_end))
            op_v = op_v.split('/')
            op_v = list(filter(None, op_v))
            ops.append(op_end)
            ops_v.append(op_v)

        return ops, ops_v

    def _selective_autocomplete_without_version(self, ops, args, incomplete):
        '''Iterate available commands based on provided arguments.'''

        # Validate endpoint
        returnable_ops = self._get_returnable_ops(ops, args)

        if returnable_ops != []:

            # Filter ops for valid args
            returnable_ops = self._filter_returnable(returnable_ops, args)
            comp = self._match_incomplete(returnable_ops, incomplete)
        else:
            comp = []
        return comp

    def _get_returnable_ops(self, ops, args):
        '''Matches available operations based on provided args.'''

        new_ops = ops
        flag = ''

        for i in range(0, len(args)):
            ops = new_ops
            new_ops = []
            for op in ops:
                if i < len(op) and i < len(args):
                    if args[i] == op[i]:
                        new_ops.append(op)
                        if i == len(args)-1:
                            flag = 'not_flex'
                    elif re.search('\{*id\}', op[i]):
                        if flag != 'not_flex':
                            new_ops.append(op)

        return new_ops

    def _filter_returnable(self, ops, args):
        '''Filter the operations that are smaller than size of args .'''
        returnable_ops = []
        n = len(args)

        for op in ops:
            if len(op)-1 >= n:
                returnable_ops.append(op[n])

        returnable_ops = list(set(returnable_ops))
        returnable_ops.sort()

        return returnable_ops

    def _match_incomplete(self, ops, incomplete):
        '''Provided a list, return similar strings.'''
        ops_return = []
        if incomplete != '':
            for line in ops:
                if line.startswith(incomplete):
                    ops_return.append(line)
        else:
            ops_return = ops

        return ops_return

    def _full_autocomplete_without_version(self, ops, args, incomplete):
        '''Iterate only first level of availabel operations .'''
        returnable_ops = []
        ops_return = []

        for op in ops:
            returnable_ops.append(op[0])

        returnable_ops = list(set(returnable_ops))
        returnable_ops.sort()

        if incomplete != '':
            for line in returnable_ops:
                if line.startswith(incomplete):
                    ops_return.append(line)
        else:
            ops_return = returnable_ops

        return ops_return

    def cli_execute(self, endpoint='', method='', version='', data={}, query='', info=False):
        '''
        Method to translate arguments into rbkcli methods
    
        The available methods for rbkcli are:
        -execute() # For API requests
        -info() # For summarized info about the provided API
        '''
        if isinstance(endpoint, str):
            endpoint = [endpoint]

        if info:
            result = self.rbk_target.target.information(' '.join(endpoint), method=method)
        else:            
            result = self.rbk_target.target.execute(' '.join(endpoint),
                                        version=version, 
                                        method=method,
                                        data=data,
                                        param=query)

        return self.format_response(result)

    def format_response(self, result):
        '''
        Format the output of the API command.
    
        Tests the format of the output and provide it to the click cli, accordingly. 
        '''

        # Try to load as json, if possible create json output.
        try:
            json_dict = json.loads(result.text)
            response = json.dumps(json_dict, indent=2, sort_keys=True)
        
        # If not possible, means output is some other text or empty.
        except json.decoder.JSONDecodeError:

            # If not empty then that text is provided.
            if result.text != '':
                response = result.text
            
            # If text is empty provide Response code, for clarity.
            else:
                response = str('Response code: ' + str(result.status_code) + 
                               '\nResponse text: ' + result.text)

        return response
