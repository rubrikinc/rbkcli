"""rbkcli report table Printer"""

import json

from rbkcli import RbkCliBlackOps, RbkcliException


class JsonfyReportTable(RbkCliBlackOps):
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
    endpoint = '/jsonfy/report_table'
    description = str('Rbkcli command that generates a printed table from'
                      ' /internal/report/{id}/table.')
    summary = 'Generate rubrik report table'
    parameters = [
        {
            'name': 'report_id',
            'description': 'ID of the report to get the table from',
            'in': 'body',
            'required': True,
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
        # Treat the parameter expected, if not provided raise error.
        if 'file' not in args.parameters.keys():
            raise RbkcliException.ScriptError('Missing Arguments.')

        # Build request to get the report table:
        if 'limit' in args.parameters.keys():
            limit = int(args.parameters.limit)
            self.request.parameter = json.dumps({'limit': limit})
        self.request.method = 'post'
        self.request.api_endpoint = ['report',
                                     args.parameters.report_id,
                                     'table']

        # Get the report table
        report_json = self.rbkcli.callit(self.request)

        # Convert it to a json output
        table_json = []
        for line in report_json['dataGrid']:
            line_json = {}
            for row in enumerate(line):
                line_json[report_json['columns'][row[0]]] = row[1]
            table_json.append(line_json)

        return table_json
