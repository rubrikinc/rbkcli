"""Input Handler module for rbkcli."""

import re

from rbkcli.base import CONSTANTS, RbkcliException
from rbkcli.core.handlers import ApiTargetTools


class InputHandler(ApiTargetTools):
    """
    Handle all the API and endpoint listing, connects with the ApiHandler.

    Available fields to be passed to cluster.order() are:
        self.req = req
        self.req.endpoint = ''
        self.req.version = ''
        self.req.method = ''
        self.req.parameter = {}
        self.req.data = {}
        self.req.formatt = ''
    This class will make sure each of those fields are valid.
    """

    def __init__(self, base_kit, operations):
        """Initialize InputHandler class."""
        ApiTargetTools.__init__(self, base_kit)

        self.req = self.dot_dict()
        self.req_ops = self.dot_dict()
        self.operations = operations
        self.error = ''

    def convert(self):
        """Place holder for future method."""

    def validate(self, req):
        """Validate the request format and consistency to be able to exec."""
        # Atributing to its own req instance as dot dict.
        self._assing_request(req)

        # Transfor endpoint to list and remove possible provided version.
        self._normalize_endpoint()
        self._extract_version_inline()

        if not self._is_valid_endpoint():
            error = 'The provided endpoint is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error + ' ' + self.error)

        if not self._is_valid_version():
            error = 'The provided version is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        if not self._is_valid_method():
            error = 'The provided method is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        if not self._is_valid_data():
            error = 'The provided data is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        if not self._is_valid_query():
            error = 'The provided query is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        if self.req.formatt not in CONSTANTS.SUPPORTED_OUTPUT_FORMATS:
            error = 'The requested formatt is invalid.'
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        if self.req.endpoint_key == []:
            error = str('Could not find any available command with'
                        ' the provided combination of method and endpoint.')
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        # Assuming validation was completed successfully, logging n returning.
        msg = str('Rbkcli # Validation succeeded for provided arguments [%s]'
                  % self.req_ops.simple_dict_natural())
        self.rbkcli_logger.debug(msg)
        return self.req

    def _is_valid_endpoint(self):
        """Confirm if provided endpoint is valid."""
        if not self._split_endpoint_arguments():
            return False
        if not self._gen_endpoint_key():
            return False

        # If normalization fails, fail the validation.
        if not isinstance(self.req.endpoint, str):
            return False

        return True

    def _split_endpoint_arguments(self):
        """Split and parse provided endpoint."""
        self.req.not_verified = []

        self.req.endpoint_parsed = self.req.endpoint.copy()
        while not self._match_endpoint() and self.req.endpoint_parsed != []:
            self.req.not_verified.append(self.req.endpoint_parsed[-1])
            self.req.endpoint_parsed.pop(-1)

        self.req.not_verified.reverse()
        self.req.endpoint = '/'.join(self.req.endpoint_parsed)
        self.req.endpoint_matched = '/' + '/'.join(self.req.endpoint_matched)
        self.req.endpoint_search = str(self.req.version + ':' +
                                       self.req.endpoint_matched +
                                       ':' + self.req.method)

        if self.req.not_verified != []:
            error = str('There are arguments that could not be parsed [%s].' %
                        " ".join(self.req.not_verified))
            msg = 'RbkcliError # ' + error
            self.error = error
            self.rbkcli_logger.error(msg)
            return False

        return True

    def _gen_endpoint_key(self):
        """Generate endpoint key for request."""
        # Using the matched endpoint get the endpoint key.
        self.req.endpoint_key = []
        for line in self.operations.ops:
            if self.req.endpoint_search in line:
                self.req.endpoint_key.append(line)

        # If endpoint key is empty logg error and return false.
        if self.req.endpoint_key == []:
            error = str('Unable to find any endpoint and method combination '
                        'that matches the provided [%s].' %
                        (self.req.endpoint_search))
            msg = 'RbkcliError # ' + error
            self.error = error
            self.rbkcli_logger.error(msg)
            return False

        return True

    def _match_endpoint(self):
        """Parse and match endpoint with the available list."""
        self.req.endpoint_matched = ''
        for auth_edpt in self.operations.ops:
            auth_edpt = auth_edpt.split(':')
            auth_end = auth_edpt[1].split('/')
            auth_end = list(filter(None, auth_end))

            for block in enumerate(auth_end):
                if block[0] <= len(self.req.endpoint_parsed) - 1:
                    if (block[1] == self.req.endpoint_parsed[block[0]] or
                            re.search('{*id}', block[1])):

                        if (block[0] == len(self.req.endpoint_parsed) - 1 and
                                len(auth_end) == len(
                                    self.req.endpoint_parsed)):

                            self.req.endpoint_matched = auth_end
                            return True
                    else:
                        break
        return False

    def _normalize_endpoint(self):
        """Convert endpoint to list, without API version inline."""
        # Convert from list to string.
        if isinstance(self.req.endpoint, list):
            self.req.endpoint = " ".join(self.req.endpoint)

        # Treat wrong syntax.
        if '?' in self.req.endpoint and ' ' in self.req.endpoint:
            error = str('Unsupported syntax, "?" can only be used for queries'
                        ', with endpoints entered as URL')
            msg = 'RbkcliError # ' + error
            self.rbkcli_logger.error(msg)
            raise RbkcliException.RbkcliError(error)

        # Remove inline parameters:
        if '?' in self.req.endpoint:
            self.req.endpoint = self.req.endpoint.strip().split('?')
            self.req.inline_query = '?' + self.req.endpoint[1]
            self.req.endpoint = self.req.endpoint[0]
        else:
            self.req.inline_query = ''

        # If its string, treat cases of space/slash separated arguments.
        if isinstance(self.req.endpoint, str):
            if ' ' in self.req.endpoint and '/' in self.req.endpoint:
                error = str('Unsupported syntax, when entering endpoints as'
                            ' URLs no (" ") is supported')
                msg = 'RbkcliError # ' + error
                self.rbkcli_logger.error(msg)
                raise RbkcliException.RbkcliError(error)

            if ' ' in self.req.endpoint:
                self.req.endpoint = self.req.endpoint.strip().split(' ')
            elif '/' in self.req.endpoint:
                self.req.endpoint = self.req.endpoint.strip().split('/')
            else:
                self.req.endpoint = [self.req.endpoint]

        # Remove empty elements from list.
        self.req.endpoint = list(filter(None, self.req.endpoint))

    def _extract_version_inline(self):
        """Parse and attribute version from endpoint."""
        # Verify if version was provided with endpoint
        if self.req.endpoint[0] in CONSTANTS.SUPPORTED_API_VERSIONS:

            # If it was, store that version in another var and remove from-
            # endpoint variable
            self.req.inline_version = self.req.endpoint[0]
            self.req.endpoint.pop(0)

        # If not in endpoint then inline is consider same as provided version.
        else:
            self.req.inline_version = self.req.version

    def _is_valid_version(self):
        """Confirm if provided version is valid."""
        # Get the version from the endpoint matched.
        self.req.key_version = self.req.endpoint_key[0].strip().split(':')
        self.req.key_version = self.req.key_version[0]

        # If both inline and provided versions are blank, use the found one.
        if self.req.version == '' and self.req.inline_version == '':
            self.req.version = self.req.key_version

        # If only the provided version is empty, confirm if the remaining-
        # ones match.
        elif self.req.version == '':
            if self.req.key_version != self.req.inline_version:
                return False
            self.req.version = self.req.key_version

        # If only the inline version is empty, confirm if the remaining-
        # ones match.
        elif self.req.inline_version == '':
            if self.req.key_version != self.req.version:
                return False

        # If final received validation is not in the instanciated versions,
        # it fails the test.
        if self.req.version not in self.operations.apis_to_instantiate:
            return False

        # Assuming all ifs passes, validation is succeeded.
        return True

    def _is_valid_method(self):
        """Confirm if provided method is valid."""
        if (self.req.method not in
                CONSTANTS.SUPPORTED_USER_METHODS['dev']):
            return False
        return True

    def _is_valid_data(self):
        """Confirm if provided data is valid."""
        if '{' not in self.req.data and not isinstance(self.req.data, dict):
        #if not isinstance(self.req.data, dict):
            data_ops = self.json_ops()
            self.req.data = data_ops.natural_simple_dictstr(self.req.data)


        return True

    def _is_valid_query(self):
        """Confirm if provided query is valid."""
        # If parameter is a list, treat it like a string.
        if isinstance(self.req.param, list):
            self.req.param = ' '.join(self.req.param)
        # For query entered with comma separated arguments replace with &.
        self.req.param = self.req.param.replace(',', '&')

        # If both inline query and CLI query are entered concatenate them.
        if self.req.inline_query == '':
            if self.req.param != '':
                if not self.req.param.startswith('?'):
                    self.req.param = '?' + self.req.param
        elif self.req.param != '':
            self.req.param = '&' + self.req.param

        return True

    def _assing_request(self, req):
        """Create instance request as dot dict."""
        for key in req.keys():
            self.req[key] = req[key]
            if key == 'documentation_objct':
                req[key] = ''
        self.req_ops = self.json_ops(req)