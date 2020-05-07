"""Callback module for rbkcli."""

import json

from rbkcli.core.handlers.inputs import InputHandler
from rbkcli.base.essentials import DotDict, RbkcliException
from rbkcli.core.handlers import ApiTargetTools
from rbkcli.core.handlers.outputs import OutputHandler

class CallBack(ApiTargetTools):
    """Class to provide rbkcli internal api calls."""
    def __init__(self, operations, base_kit):
        """Initialize callback class."""
        ApiTargetTools.__init__(self, base_kit)
        self.operations = operations
        self.base_kit = base_kit
        self.validator = InputHandler(self.base_kit, self.operations)
        self.formatter = OutputHandler(base_kit, self.operations)

    def parseit(self, args):
        """Parse arguments provided."""
        self.args = args

        if not isinstance(self.args, list):
            self.args = self.args.replace('rbkcli ', '')
            
            new_args = []
            self.args = self.args.split('"')
            if len(self.args) % 2 != 0:
                for arg in enumerate(self.args):
                    newarg = arg[1]
                    if arg[0] % 2 == 0:
                        newarg = arg[1].split()
                    if isinstance(newarg, list):
                        new_args = new_args + newarg
                    else:
                        new_args.append(newarg)
            else:
                print('Error ## Danger, danger, high voltage...')

            self.args = new_args

        self.request = self.base_kit.parser.parse_args(self.args)
        self.request = vars(self.request)
        self.request = self.base_kit.parser.un_list(self.request)

        return self.request, self.args

    def structreit(self, args, request):
        """Reestructure arguments provided."""
        self.args = args
        self.request = {}
        requet_1 = {}
        for key in request.keys():
            self.request[key] = request[key]
            requet_1[key] = request[key]

        # Structure the request to the needed format.
        stct_request = self.base_kit.parser.create_request_structure(requet_1, self.args)

        # Pass data to dot dictionary
        self.stct_request = DotDict()
        for key in stct_request.keys():
            self.stct_request[key] = stct_request[key]

        # Normalizing request dictionary
        self.stct_request.endpoint = ' '.join(self.stct_request.api_endpoint)
        self.stct_request.formatt = 'raw'
        self.stct_request.param = self.stct_request.query
        self.stct_request.data = self.stct_request.parameter
        self.stct_request.structured = True

        return self.stct_request

    def callit(self, stct_request, args=None):
        """Call endpoint provided with arguments."""
        if 'structured' not in stct_request.keys():
            if args is None:
                args = []
            stct_request = self.structreit(args, stct_request)
        self.stct_request = stct_request

        self.req = self.validator.validate(self.stct_request)
        api_result = self.operations.execute(self.req)

        if '{' in api_result.text or '[' in api_result.text:
            try:
                self.call_result = json.loads(api_result.text)
            except:
                self.call_result = { 'result_text': api_result.text}
        else:
            self.call_result = { 'result_text': api_result.text}

        return self.call_result

    def call_back(self, args):
        """Perform same level of parsing (even CLI) as any other request."""
        self.request, self.args = self.parseit(args)
        self.stct_request = self.structreit(self.args, self.request)

        result = DotDict()
        result.text = self.callit(self.stct_request)
        result.status_code = 200
        result.text = json.dumps(result.text, indent=2)

        return self.formatter.outputfy(self.req, result)

    def call_back_text(self, args):
        """Returns dict directly instead of API result."""
        result = self.call_back(args)
        return json.loads(result.text)
