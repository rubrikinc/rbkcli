"""rbkcli report table Printer"""

import json

from rbkcli import RbkCliBlackOps


class JsonfyReportTable(RbkCliBlackOps):
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
        # Treat the parameter expected, if not provided save it to local.
        if 'report_id' not in args.parameters.keys():
            raise Exception('Missing args')

        # 1- Get the report table:
        if 'limit' in args.parameters.keys():
            limit = int(args.parameters.limit)
            self.request.parameter = json.dumps({'limit': limit})
        self.request.method = 'post'
        self.request.api_endpoint = ['report',
                                     args.parameters.report_id,
                                     'table']
        report_json = self.rbkcli.callit(self.request)

        # Convert it to a json output
        table_json = []
        for line in report_json['dataGrid']:
            line_json = {}
            for row in enumerate(line):
                line_json[report_json['columns'][row[0]]] = row[1]
            table_json.append(line_json)

        return table_json
