"""rbkcli convert csv to json"""

from rbkcli import RbkCliBlackOps, RbkcliException


class JsonfyCsv(RbkCliBlackOps):
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

        # Open the provided csv file.
        try:
            with open(args.parameters.file, 'r') as csv:
                csv_content = csv.readlines()
        except FileNotFoundError as error:
            self.rbkcli_logger.error(error)
            raise RbkcliException.ScriptError(error)

        # Declare the returning elements.
        list_dict = []
        each_dict = {}
        keys = []

        # Loop through the csv file.
        for line in enumerate(csv_content):

            # Use first line, usually the column index as keys.
            if line[0] == 0:
                keys = line[1].split(',')

            # Use all other lines as values.
            else:
                values = line[1].split(',')

                # for each line create a dictionary with the keys and values.
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
