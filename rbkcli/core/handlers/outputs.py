"""Output Handler module for rbkcli."""

import json
import re

from rbkcli.base import CONSTANTS, RbkcliException
from rbkcli.core.handlers import ApiTargetTools
from rbkcli.base.jsops import MapResponseDoc
from rbkcli.core.handlers.jsometa import JsonSelection, JsonEditor

# This will be instantiated as soon as the target is instantiated.
# It will have 2 different workflows, one in wich the API is run and the output of it needs to be modified.
# The other when prior to running the API it requests the available keys.
    # If the available keys are documented under a schema then we use that to provide available keys.
    # If not available then we run the API and based on the result create the key map.

# To successfully direct the workflow for this we need treat the requests correctly.
# -> Every request that does not have a documentation will be executed to be mapped.
# -> Every map request will interrupt the workflow, returning the map


class OutputHandler(ApiTargetTools):
    """
    Class that analyze and modify outputs.

    Changes are done based on the parameters provided by the user.
    """

    def __init__(self, base_kit, operations):
        """Initialize InputHandler class."""
        ApiTargetTools.__init__(self, base_kit)
        self.operations = operations
        self.req = self.dot_dict()
        self.result = self.dot_dict()
        self.result.text = ''
        self.json_iter = self.dot_dict()

    def available_fields(self, req):
        """Provide available fields to select or filter in a json."""
        # Atribute req to instance variable
        self.req = req

        if not self._is_response_documented():
            if not self._is_api_mappable():
                raise Exception('The output of this  API is not a json')

        self._gen_string_result()

        return self.result.text

    def _is_response_documented(self):
        """Validate if json response is documented and can be used."""
        # Try to load as json, if possible create json output.
        json_document = json.loads(self.req.documentation_objct)

        self.json_iter = MapResponseDoc(json_data=json_document)
        self.json_iter.iterit()

        if self.json_iter.map.full != []:
            return True

        return False

    def _is_api_mappable(self):
        """Validate if json result can be mapped."""
        json_result = self.operations.execute(self.req)

        try:
            json_result = json.loads(json_result.text)
        except json.decoder.JSONDecodeError:
            return False

        # Changing it.
        selection = JsonEditor(json_result, [], self.rbkcli_logger)
        self.json_iter.map = selection.model_map()

        return True

    def _gen_string_result(self):
        """Generate a string with all the available fields."""
        key_query = {
            '?': 'simple_keys',
            '?NK': 'nested_keys',
            '?MAP': 'full',
        }
        
        query_provided = self.req.output_workflow[0]['value']

        try:
            return_keys = self.json_iter.map[key_query[query_provided]]
        except Exception as e:
            print(e)

        final_return_keys = ''
        end = '\n'
        for line in enumerate(return_keys):
            final_return_key = ''
            if line[0] == len(return_keys) - 1:
                end = ''

            return_key = line[1].split(']')
            for key in return_key:
                if key != '':
                    key = key.replace('[', '')
                    key = key.split('#')
                    key = key[0]
                    final_return_key = final_return_key + '[' + key + ']'

            final_return_keys = final_return_keys + final_return_key + end

        self.result.text = final_return_keys

    def outputfy(self, req, output):
        """Request the correct output convertion."""
        self.req = req
        self.output_workflow = req.output_workflow
        self.result = output

        self.selection = None
        for line in enumerate(self.output_workflow):

            self.treat_field(line[0], line[1]['arg'], line[1]['value'])

        if self.req.table:
            if self.selection is None:
                self.treat_field(0, 'filter', 'a')
            self.result.text = self.selection.convert_to_table()
        if self.req.list:
            if self.selection is None:
                self.treat_field(0, 'filter', 'a')
            self.result.text = self.selection.convert_to_list()
        if self.req.pretty_print:
            if self.selection is None:
                self.treat_field(0, 'filter', 'a')
            self.result.text = self.selection.convert_to_prettyprint()


        return self.result

    def treat_field(self, ix, action, act_value):
        """Perform the json modification requested."""
        json_dict = json.loads(self.result.text)
        if isinstance(json_dict, dict) or isinstance(json_dict, list):
            fields_model = []
            if ix == 0:
                fields_model = self.operations.documentation(self.req)
                fields_model = fields_model.text

            self.selection = JsonSelection(json_dict,
                                           fields_model,
                                           self.operations,
                                           self.base_kit)
            if action == 'select':
                output = self.selection.select(act_value)
            elif action == 'filter':
                output = self.selection.filter(act_value)
            elif action == 'context':
                output = self.selection.context(act_value)
            elif action == 'loop':
                output = self.selection.loop(act_value)

        self.result = self.dot_dict()
        if isinstance(output, str):
            self.result.text = output
        else:
            self.result.text = json.dumps(output, indent=2)
