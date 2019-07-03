"""Essential module, parameters shared for rbkcli."""

import os

BASE_FOLDER = os.path.expanduser('~/rbkcli')
TARGETS_FOLDER = BASE_FOLDER + '/targets'
CONF_FOLDER = BASE_FOLDER + '/conf'
LOGS_FOLDER = BASE_FOLDER + '/logs'
SUPPORTED_API_VERSIONS = ['v1',
                          'v2',
                          'internal',
                          'adminCli',
                          'rbkcli',
                          'cmdlets',
                          'scripts']
SUPPORTED_API_METHODS = ['head',
                         'get',
                         'post',
                         'put',
                         'patch',
                         'delete']
USERS_PROFILE = ['dev', 'admin', 'support']
SUPPORTED_USER_METHODS = {
    'admin': ['get'],
    'support': SUPPORTED_API_METHODS,
    'dev': SUPPORTED_API_METHODS
}
SUPPORTED_OUTPUT_FORMATS = ['raw',
                            'json',
                            'table',
                            'list',
                            'values']
CONF_DICT = {}


class DotDict(dict):
    """Create a dictionary managed/accessed with dots."""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CONSTANTS = DotDict({
    'BASE_FOLDER': BASE_FOLDER,
    'TARGETS_FOLDER': TARGETS_FOLDER,
    'CONF_FOLDER': CONF_FOLDER,
    'LOGS_FOLDER': LOGS_FOLDER,
    'SUPPORTED_API_VERSIONS': SUPPORTED_API_VERSIONS,
    'SUPPORTED_API_METHODS': SUPPORTED_API_METHODS,
    'USERS_PROFILE': USERS_PROFILE,
    'SUPPORTED_USER_METHODS': SUPPORTED_USER_METHODS,
    'SUPPORTED_OUTPUT_FORMATS': SUPPORTED_OUTPUT_FORMATS,
    'CONF_DICT': CONF_DICT
})


class RbkcliException(Exception):
    """Customize Rbkcli exceptions."""

    class ApiRequesterError(Exception):
        """Customize DynaTable exceptions."""

    class DynaTableError(Exception):
        """Customize DynaTable exceptions."""

    class ToolsError(Exception):
        """Customize RbkcliTools exceptions."""

    class LoggerError(Exception):
        """Customize RbkcliLogger exceptions."""

    class ClusterError(Exception):
        """Customize RbkcliLogger exceptions."""

    class ApiHandlerError(Exception):
        """Customize DynaTable exceptions."""

    class RbkcliError(Exception):
        """Customize DynaTable exceptions."""