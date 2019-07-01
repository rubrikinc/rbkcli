"""Module for advanced json operations."""

import copy
import json

from rbkcli.core.handlers import ApiTargetTools

try:
    #from rbkcli.core.handlers.callback import CallBack
    import rbkcli.core.handlers.callback
except Exception as e:
    print(e)

from rbkcli.base.essentials import DotDict, RbkcliException
from rbkcli.base.jsops import DynaTable, MapResponseDoc
from rbkcli.base.jsops import MapSelect, PrettyPrint


class JsonEditor():
    """Select specific keys and or filter the values desired."""

    def __init__(self, json_data, fields_model, rbkcli_logger):
        """Initialize json selection."""
        # Initialize var for fields requested.
        self.final_fields_order = []
        self.rbkcli_logger = rbkcli_logger

        # Validate json data provided
        self.json_data = self._validate_json(json_data)

        # If there is a data key by default we get its content
        ## FIX Might want to add a configuration to choice for detault
        if isinstance(self.json_data, dict):
            if 'data' in self.json_data.keys():
                self.json_data = self.json_data['data']


        self.fields_model = self._validate_json(fields_model, type_='model')

        # Convert fields_model into metadata_map if provided.
        self.model_map()

    def _validate_json(self, json_data, type_='data'):
        """Validate that data is json, if not return empty."""
        # Test provided data type.
        if not isinstance(json_data, dict) and not isinstance(json_data, list):
            try:
                json_data = json.loads(json_data)
            except json.decoder.JSONDecodeError:
                # If not able to json load the data, then attribute empty.
                json_data = {}

            # If data is empty then raise exception.
            if (json_data == {} or json_data == [] and type_ != 'model'):
                raise Exception('Json data can not be empty')

        return json_data

    def model_map(self):
        """Generate map from json model to allow verification."""
        # Get a map from the json provided.
        #print(self.fields_model)
        table_order = []
        if self.fields_model == {} or self.fields_model == []:
            json_iter = MapSelect(definitions=[],
                                  json_data=self.json_data)
            #print('try and map me')
        else:
            # Verifies if the documentation provided covers the schema of response.
            two_hundred = self.fields_model['doc']['responses']['200']
            schema = two_hundred['schema']
            if 'table_order' in two_hundred.keys():
                table_order = two_hundred['table_order']

            if schema == {}:
                json_iter = MapSelect(definitions=[],
                                      json_data=self.json_data)
            else:
                json_iter = MapResponseDoc(json_data=self.fields_model)

        self.json_map = json_iter.mapit()
        self.json_map.table_order = table_order
        #print(self.json_map)
        return self.json_map

    def new_model(self, json_data, fields_model=[]):
        """Overwrite model for verification."""
        self.json_data = json_data
        self.fields_model = self._validate_json(fields_model)
        #print(self.json_data)
        #print(self.fields_model)
        self.model_map()

    def _validate_req_fields(self):
        """Validate and normalize fields provided."""
        # If there is a comma in the requested fields, split it.
        fields = self.req_fields
        if ',' in self.req_fields:
            fields = self.req_fields.split(',')
        # If the fields are not a list and does not have a comma, convert it.
        elif not isinstance(self.req_fields, list):
            fields = [self.req_fields]

        if fields[0].startswith('?'):
            self.selected_data = self._get_available_fields(fields)
            return False

        # Create final
        self._request_creator(fields)
        return True

    def _get_available_fields(self, fields, mode='print'):
        key_query = {
            '?': 'simple_keys',
            '?NK': 'nested_keys',
            '?MAP': 'full',
        }
        if fields[0] in key_query.keys():
            return_keys = self.json_map[key_query[fields[0]]]
        else:
            return_keys = []
        if mode == 'print':
            final_return_keys = ''
        else:
            final_return_keys = []
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
                    if mode == 'print':
                        final_return_key = final_return_key + '[' + key + ']'
                    else:
                        final_return_key = final_return_key + key
            if mode == 'print':
                final_return_keys = final_return_keys + final_return_key + end
            else:
                final_return_keys.append(final_return_key)

        return final_return_keys


    def _request_creator(self, fields):
        """
        Generate final request dictionary.

        The challenge here is to keep the order provided when returning the
        results. Dictionary data type does not keep an order, so we have to
        use a list to effectively retain the requested order.
        """
        # Define temporary variable.
        final = {}
      
        # Split field and filter from provided data.
        for field_filter in enumerate(fields):
            counter = 1
            field = field_filter[1]
            final_field = field
            filter_ = ''
            filter_contain = ''
            filter_not = ''
            filter_not_contain = ''

            if '!=' in field:
               field = field.split('!=')
               filter_not = field[1]
            elif '!~' in field:
               field = field.split('!~')
               filter_not_contain = field[1]
            elif '~' in field:
               field = field.split('~')
               filter_contain = field[1]

            elif '=' in field:
               field = field.split('=')
               filter_ = field[1]
            else:
                field = [field]

            field = field[0]
            final_field = field

            
            final_field = self._reformat_nested_ks(final_field)
            # If user provided duplicated fields create '<field>_<n>' key.
            while final_field in final.keys():
                counter = counter + 1
                final_field = final_field.split('_')
                final_field = final_field[0]
                final_field = final_field + '_' + str(counter)
            
            # Make sure the order which request was mande is kept in a list.
            self.final_fields_order.append(final_field)

            # Create the final_fields dictionary to pass for parsing,
            # using the map gathered before.
            final[final_field] = {
                'dictKey': self._get_field_key(field),
                'filter_eq': filter_,
                'filter_aprox': filter_contain,
                'filter_not': filter_not,
                'filter_not_aprox': filter_not_contain
            }

            # If a keys requested is not validated remove the key.
            if final[final_field]['dictKey'] is None:
                del final[final_field]

        # Attribute it to instance variable.
        self.final_fields = final
        #print(final)

    def _reformat_nested_ks(self, fields):
        fields = fields.replace('][', '_')
        fields = fields.replace(']', '')
        fields = fields.replace('[', '')
        return fields


    def _get_field_key(self, field):
        """Match provided field with existing mapped field."""
        # This needs to be reviewed and completed.
        #print(field)
        if '[' not in field:
            for valid_field in self.json_map.full:
                if valid_field.startswith('['+field+'#'):
                    #print(valid_field)
                    return valid_field
        else:
            req_field = field.split(']')
            req_field.pop(-1)
            result_field = None
            for valid_field in self.json_map.full:
                val_fields = valid_field.split(']')
                val_fields.pop(-1)
                #print(req_field)
                #print(val_fields)
                if len(req_field) == len(val_fields):
                    for fld in enumerate(req_field):
                        #print(fld[1] + '#')
                        #print(val_fields[fld[0]])
                        if not val_fields[fld[0]].startswith(fld[1] + '#'):
                            break
                        elif val_fields[fld[0]].startswith(fld[1] + '#'):
                            if len(req_field) == fld[0]+1:
                                result_field = valid_field
                        #if fld[1] == val_fields[fld[0]]
            #print(result_field)
            #print(result_field)
            return result_field


    def iterate(self, req_fields):
        """Get the selected fields from json data."""
        # Atribute provided selection var to instance var.
        self.req_fields = req_fields

        # Validate the fields provided.
        if not self._validate_req_fields():
            return self.selected_data

        # Select the data.
        self.selected_data = self._iterate_json()

        return self.selected_data

    def _iterate_json(self):
        """."""
        if isinstance(self.json_data, dict):
            selected_data = self._iterate_dict()
        elif isinstance(self.json_data, list):
            selected_data = self._iterate_list()

        return selected_data

    def _iterate_list(self):
        """."""
        selected_data = []
        for objct in self.json_data:
            selection = MapSelect(definitions=self.final_fields,
                                  json_data=[objct])
            selected_objct = selection.iterit()
            if selected_objct != {}:
                selected_data.append(selected_objct)

        return selected_data
        
    def _iterate_dict(self):
        """."""
        selection = MapSelect(definitions=self.final_fields,
                              json_data=self.json_data)
        return selection.iterit()

    def convert_to_table(self):
        self.filled_worked = self.selected_data
        body = []
        for head in self.final_fields_order:
            row = []

            if isinstance(self.filled_worked, dict):
                if 'data' in self.filled_worked.keys():
                    self.filled_worked = self.filled_worked[data]
                    for objt in self.filled_worked:
                        try:
                            line = objt[head]
                        except Exception:
                            line = 'N/E'
                        line = str(line)
                        row.append(line)

                else:
                    line = self.filled_worked[head]
                    line = str(line)
                    row.append(line)

            elif isinstance(self.filled_worked, list):
                for objt in self.filled_worked:
                    try:
                        line = objt[head]
                    except Exception:
                        line = 'N/E'
                    line = str(line)
                    row.append(line)

            body.append(row)

        headers = self.final_fields_order
        summary = 'Total amount of objects'
        table = DynaTable(headers, body, summary=summary)
        
        #table.print_table()
        table_str = ''
        try:
            table_lst = table.assemble_table()
        except IndexError as error:
            msg = 'No results returned, canno\'t create table...'
            self.rbkcli_logger.error('DynamicTableError # ' + msg)
            raise RbkcliException.DynaTableError(msg + '\n')

        for line in table_lst:
            table_str = table_str + line + '\n'

        return table_str

    def convert_to_list(self):
        self.filled_worked = self.selected_data
        table_str = ''

        if isinstance(self.filled_worked, dict):
            table_str = self._dict_list_table(self.filled_worked)
        elif isinstance(self.filled_worked, list):
            for dict_ in self.filled_worked:
                table_str_l = self._dict_list_table(dict_)
                table_str = table_str + '\n' + table_str_l

        return table_str

    def _dict_list_table(self, dict_):
        header = ['key', 'value']
        key_row = []
        value_row = []

        for key, value in dict_.items():
            key_row.append(key)
            value_row.append(str(value))

        body = [key_row, value_row]
        summary = 'Total amount of objects'
        table = DynaTable(header, body, summary=summary)
        
        table_str = ''
        try:
            table_lst = table.assemble_table()
        except IndexError as error:
            msg = 'No results returned, canno\'t create table...'
            self.rbkcli_logger.error('DynamicTableError # ' + msg)
            raise RbkcliException.DynaTableError(msg + '\n')
        for line in table_lst:
            table_str = table_str + line + '\n'

        return table_str


    def convert_to_list1(self):
        self.filled_worked = self.selected_data
        body = []
        for head in self.final_fields_order:
            row = []

            if isinstance(self.filled_worked, dict):
                if 'data' in self.filled_worked.keys():
                    self.filled_worked = self.filled_worked[data]
                    for objt in self.filled_worked:
                        line = objt[head]
                        line = str(line)
                        row.append(line)

                else:
                    line = self.filled_worked[head]
                    line = str(line)
                    row.append(line)

            elif isinstance(self.filled_worked, list):
                for objt in self.filled_worked:
                    line = objt[head]
                    line = str(line)
                    row.append(line)
            body.append(row)

        headers = self.final_fields_order
        summary = 'Total amount of objects'
        table = DynaTable(headers, body, summary=summary)
        
        #table.print_table()
        table_str = ''
        try:
            table_lst = table.assemble_table()
        except IndexError as error:
            msg = 'No results returned, canno\'t create table...'
            self.rbkcli_logger.error('DynamicTableError # ' + msg)
            raise RbkcliException.DynaTableError(msg + '\n')
        for line in table_lst:
            table_str = table_str + line + '\n'

        return table_str

    def convert_to_prettyprint(self):

        pprint_inst = PrettyPrint(json_data= self.selected_data)
        return pprint_inst.iterit()

class JsonFilter(JsonEditor):
    def _get_order_keys(self):
        all_keys = []
        #print(self.json_map.table_order)
        full_keys = copy.copy(self.json_map.full)
        if self.json_map.table_order != []:
            for field in self.json_map.table_order:
                for keys in self.json_map.full:
                    if keys.startswith('[%s#' % field):
                        all_keys.append(keys)
                        full_keys.remove(keys)
                        #print(keys)
            if full_keys != []:
                all_keys = all_keys + full_keys
        else:
            all_keys = self.json_map.full

        return all_keys

    def _request_creator(self, fields):
    #def _select_request_creator(self, fields):
        """."""
        # Create a list of available 1st levels.
        # Attribute that list to a dictionary as the final result, like select_reques_creator
        # Iterate the results obeying the filter passed 
        all_keys = self._get_order_keys()
        #all_keys = self.json_map.full
        if fields[0].startswith('KEY='):
            fields = fields[0].replace('KEY=', '')
            all_keys = []
            all_keys_ = self.json_map.simple_keys
            for key in all_keys_:
                if fields in key:
                    all_keys.append(key)

        ### FIX or remove
        if fields[0].startswith('VALUE='):
            value_fields = ''
            fields = fields[0].replace('VALUE', '')
            #all_keys = []
            all_keys = self.json_map.simple_keys
            for key in all_keys:
                value_fields = value_fields + ',' + key + fields
            fields = value_fields[1:]
        ###

        first_levels = []
        final = {}
        for line in all_keys:
            line = line.split(']')
            line = line[0]
            line = line.split('#')
            line = line[0].replace('[', '')
            if line not in first_levels:
                first_levels.append(line)
                final[line] = {
                    'dictKey': self._get_field_key(line),
                    'filter_eq': '',
                    'filter_aprox': '',
                    'filter_not': '',
                    'filter_not_aprox': ''
                }

        # Split field and filter from provided data.
        for field_filter in enumerate(fields):
            counter = 1
            field = field_filter[1]
            final_field = field
            filter_ = ''
            filter_contain = ''
            filter_not_contain = ''
            filter_not = ''

            if '!=' in field:
               field = field.split('!=')
               filter_not = field[1]
            elif '!~' in field:
               field = field.split('!~')
               filter_not_contain = field[1]
            elif '~' in field:
               field = field.split('~')
               filter_contain = field[1]

            elif '=' in field:
               field = field.split('=')
               filter_ = field[1]
            else:
                field = [field]

            field = field[0]
            final_field = field


            # Create the final_fields dictionary to pass for parsing,
            # using the map gathered before.
            final[final_field] = {
                'dictKey': self._get_field_key(field),
                'filter_eq': filter_,
                'filter_aprox': filter_contain,
                'filter_not': filter_not,
                'filter_not_aprox': filter_not_contain
            }

            # If a keys requested is not validated remove the key.
            if final[final_field]['dictKey'] is None:
                del final[final_field]

        # Make sure the order which request was mande is kept in a list.
        self.final_fields_order = first_levels

        #print(final)
        # Attribute it to instance variable.
        self.final_fields = final

class JsonLooper(JsonEditor):

    def _iterate_list(self):
        """."""
        selected_data = []
        for objct in self.json_data:
            selection = MapSelect(definitions=self.final_fields,
                                  json_data=[objct])
            selected_objct = selection.iterit()
            if selected_objct != {}:
                result = self._call_api(selected_objct)
                ### NEEDS TESTING AF
                selected_data = list_protection(result, selected_data)
                #selected_data.append(result)

        return selected_data
        
    def _iterate_dict(self):
        """."""
        selection = MapSelect(definitions=self.final_fields,
                              json_data=self.json_data)
        result = selection.iterit()
        result_1 = self._call_api(result)
        return result_1

    def _call_api1(self, fields_selected):
        content = fields_selected[self.loop_key]
        api_to_run = self.loop_api.replace('{' + self.loop_key + '}', content)
        result_dict = self.cbacker.call_back(api_to_run)
        result_dict = json.loads(result_dict.text)
        for key, value in fields_selected.items():
            result_dict['loop_'+key] = value

        return result_dict

    def _call_api(self, fields_selected):
        final_result_dict = []
        try:
            #print('Fields selected: ' + str(fields_selected))
            #print('Loop key' + self.loop_key)
            content = fields_selected[self.loop_key]
        except KeyError:
            api_to_run = self.loop_api
            content = []

        if not isinstance(content, list):
            content = [content]

        new_result_dict = []

        for objct in enumerate(content):
            #api_to_run = self.loop_api.replace('{' + self.loop_key + '}', objct[1])
            if '{{' in self.loop_api:
                start_sign = '{{'
                end_sign = '}}'
            elif '{' in self.loop_api:
                start_sign = '{'
                end_sign = '}'

            api_to_run = self.loop_api.replace(start_sign + self.loop_key + end_sign, objct[1])
            api_to_run = api_to_run.replace('{', start_sign)
            api_to_run = api_to_run.replace('}', end_sign)
            #print(api_to_run)

            ## Test changes
            result_dict = self.cbacker.call_back(api_to_run)
            result_dict = json.loads(result_dict.text)

            for key, value in fields_selected.items():
                if not isinstance(value, list):
                    value = [value]

                if key == self.loop_key:
                    if isinstance(result_dict, dict):
                        result_dict['loop_' + key] = value[0]
                    elif isinstance(result_dict, list):
                        for line in enumerate(result_dict):
                            line[1]['loop_' + key] = value[0]

                else:
                    if isinstance(result_dict, dict):
                        result_dict['loop_' + key] = value[0]
                    elif isinstance(result_dict, list):
                        for line in enumerate(result_dict):
                            line[1]['loop_' + key] = value[0]

                
            ### NEEDS TESTING AF
            final_result_dict = list_protection(result_dict, final_result_dict)
            #final_result_dict.append(result_dict)

        return final_result_dict

    def _split_api_key(self):
        if '{{' in self.to_api:
            loop_key = self.to_api.split('{{')
            loop_key = loop_key[1].split('}}')
            loop_key = loop_key[0]
        elif '{' in self.to_api:
            loop_key = self.to_api.split('{')
            loop_key = loop_key[1].split('}')
            loop_key = loop_key[0]
        else:
            loop_key = ''


        return loop_key, self.to_api

    def loopit(self, args, cbacker):
        self.cbacker = cbacker
        self.to_api = args[1]
        #print('to api: ' + self.to_api)
        self.loop_key, self.loop_api = self._split_api_key()

        return self.iterate(args[0])

def list_protection(to_append, final_result):
    if isinstance(to_append, list):
        final_result = final_result + to_append
    else:
        final_result.append(to_append)

    return final_result

class JsonContextor(JsonEditor):
    def iterate(self, req_fields):
        """Get the selected fields from json data."""
        # Atribute provided selection var to instance var.
        self.req_fields = req_fields

        # Validate the fields provided.
        if not self._validate_req_fields():
            return self.selected_data

        # Select the data.
        self.selected_data = self._iterate_json()

        new_context_map = MapSelect(json_data=self.selected_data)
        self.json_map = new_context_map.mapit()
        #print(self.json_map)
        self.final_fields_order = self._get_available_fields('?', mode='')
        #print(self.final_fields_order)

        return self.selected_data

    def _iterate_list(self):
        """."""
        selected_data = []
        selection_value_lst = []
        for objct in self.json_data:
            selection = MapSelect(definitions=self.final_fields,
                                  json_data=[objct])
            selected_objct = selection.iterit()
            if selected_objct != {}:
                selection_value_lst = []
                if isinstance(selected_objct, list):
                    selection_value_lst = selection_value_lst + selected_objct
                if isinstance(selected_objct, dict):
                    for key, value in selected_objct.items():
                        if isinstance(value, list):
                            selection_value_lst = selection_value_lst + value
                        else:
                            selection_value_lst.append(value)
                selected_data = selected_data + selection_value_lst

        return selected_data
        
    def _iterate_dict(self):
        """."""
        selection_value_lst = []
        selection = MapSelect(definitions=self.final_fields,
                              json_data=self.json_data)
        selection_value = selection.iterit()
        for key, value in selection_value.items():
            if isinstance(value, list):
                selection_value_lst = selection_value_lst + value
            else:
                selection_value_lst.append(value)
        return selection_value_lst


class JsonSelection(ApiTargetTools):
    """Select specific keys and or filter the values desired."""

    def __init__(self, json_data, fields_model, operations, base_kit):
        ApiTargetTools.__init__(self, base_kit)
        self.operations = operations
        self.json_data = json_data
        self.fields_model = fields_model
        self.base_kit = base_kit

    def select(self, req_fields):
        """Get the selected fields from json data."""
        selector = JsonEditor(self.json_data, self.fields_model, self.rbkcli_logger)
        self.current_editor = selector
        return selector.iterate(req_fields)

    def filter(self, req_fields):
        """Get the selected fields from json data."""
        filterer = JsonFilter(self.json_data, self.fields_model, self.rbkcli_logger)
        self.current_editor = filterer
        return filterer.iterate(req_fields)

    def context(self, req_fields):
        """Get the selected fields from json data."""
        contextor = JsonContextor(self.json_data, self.fields_model, self.rbkcli_logger)
        self.current_editor = contextor
        return contextor.iterate(req_fields)

    def loop(self, req_fields):
        """Get the selected fields from json data."""
        self.cbacker = rbkcli.core.handlers.callback.CallBack(self.operations, self.base_kit)
        looper = JsonLooper(self.json_data, self.fields_model, self.rbkcli_logger)
        self.current_editor = looper
        return looper.loopit(req_fields, self.cbacker)

    def convert_to_table(self):
        return self.current_editor.convert_to_table()

    def convert_to_list(self):
        return self.current_editor.convert_to_list()

    def convert_to_prettyprint(self):
        return self.current_editor.convert_to_prettyprint()
