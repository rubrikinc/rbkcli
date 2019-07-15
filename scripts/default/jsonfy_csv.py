"""rbkcli csv to json"""

from rbkcli import RbkCliBlackOps


class JsonfyCsv(RbkCliBlackOps):
    method = 'get'
    endpoint = '/jsonfy/csv'
    description = str('Rbkcli command that converts csv to json, to allow '
                      'using rbkcli json tools')
    summary = 'Load CSV file as json.'
    parameters = [
            {
            'name': 'file',
            'description': 'Path of the csv file to be loaded.',
            'in': 'body',
            'required': True,
            'type': 'string'
            }
        ]

    def execute(self, args):
        # Treat the parameter expected, if not provided raise error.
        if 'file' not in args.parameters.keys():
            raise Exception('Missing args')

        # Open the provided csv file.
        with open(args.parameters.file, 'r') as csv:
            csv_content = csv.readlines()

        # Declare the returning elements.
        list_dict = []
        each_dict = {}

        # Loop through the csv file.
        for line in enumerate(csv_content):

            # Use first line, usually the column index as keys.
            if line[0] == 0:
                keys = line[1].split(',')

            # Use all other lines as values.
            else:
                values = line[1].split(',')

                # for each line create a dictionay with the keys and values.
                for pair in enumerate(keys):
                    key = pair[1].strip()
                    value = values[pair[0]].replace('\n', '').strip()
                    each_dict[key] = value

            # Append the created dictionary to a list, ignoring empty lines.
            if each_dict != {}:
                list_dict.append(each_dict)

            # Make sure dictionary is empty
            each_dict = {}

        return list_dict
