"""Init for handlers pack."""

class ApiTargetTools():
    '''Parent Class of handlers for the ApiTarget.'''

    def __init__(self, base_kit):
        '''Initialize ApiTargetTools Class, with shared context.'''
        self.base_kit = base_kit
        self.conf_dict = base_kit.config_dict
        self.rbkcli_logger = base_kit.logger
        self.tools = base_kit.tools
        self.base_folder = base_kit.base_folder
        self.dot_dict = base_kit.dot_dict
        self.target = base_kit.target
        self.api_handler = base_kit.api_handler
        self.discover_fn = base_kit.discover_fn
        self.auth = base_kit.auth
        self.user_profile = base_kit.user_profile
        self.json_ops = base_kit.json_ops
        ### Test here
        self.callback_cmd = base_kit.callback_cmd


class RbkcliResponse():
    '''Class to standarize the responses provided by Meta commands.'''

    def __init__(self, status_code=0, text='', raw=''):
        '''.'''
        self.status_code = status_code
        self.text = text
        self.raw = raw

    @classmethod
    def successfull_response(self, func):

        def response_wrapper(self, *args, **kwargs):
            self.text = func(self, *args, **kwargs)
            self.status_code = 200
            return self

        return response_wrapper
