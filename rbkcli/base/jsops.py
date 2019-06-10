"""Module for advanced json operations."""

import copy
import json

from rbkcli.base.essentials import DotDict, RbkcliException

class DynaTable():
    '''Create a dynamically sized table with summary.'''

    ROW_DIVISION_CHAR = '|'
    LINE_DIVISION_CHAR = '='

    def __init__(self, headers, rows, logger='', **kwargs):
        '''Initialize DynaTable.'''

        # Verifying if headers and rows have the same amout of objects.
        if len(headers) != len(rows) or len(headers) == 1:
            self.table = ['Error # Invalid table']

        # Assigning provided values to the class properties
        if 'ROW_DIVISION_CHAR' in kwargs.keys():
            DynaTable.ROW_DIVISION_CHAR = kwargs['ROW_DIVISION_CHAR']
        if 'LINE_DIVISION_CHAR' in kwargs.keys():
            DynaTable.LINE_DIVISION_CHAR = kwargs['LINE_DIVISION_CHAR']
        if 'summary' in kwargs.keys():
            self.summary = kwargs['summary']
        else:
            self.summary = ''

        self.logger = logger
        self.headers = headers
        self.rows = rows
        self.table = []

    def _format_rows(self):
        '''
        Based on the maximum size acquired, reformat each value of each row
        to have that size.
        '''

        try:
            rows_size = self._get_rows_size(self.headers, self.rows)
        except RbkcliException.DynaTableError:
            return False

        for i in enumerate(rows_size):
            text = self.headers[i[0]]
            size = rows_size[i[0]]
            self.headers[i[0]] = (' {text:<{size}} '.format(text=text,
                                                            size=size))
            for line in enumerate(self.rows[i[0]]):
                text = self.rows[i[0]][line[0]]
                self.rows[i[0]][line[0]] = (' {text:<{size}} '. \
                                           format(text=text, size=size))
        return True

    def assemble_table(self):
        '''
        Create and returns a 'table' list, by appending and joinning headers,
        line separator and rows.
        '''

        table = []
        line = []
        lines = []
        n_lines = len(self.rows[0])

        if not self._format_rows():
            return [str('Error: Returned data is inconsistent with table'
                        ' creation.')]
        headers = self.ROW_DIVISION_CHAR.join(self.headers)

        for i in range(n_lines):
            for line_number in self.rows:
                line.append(line_number[i])
            lines.append(self.ROW_DIVISION_CHAR.join(line))
            line = []

        line_division_size = (len(lines[0]))

        table.append(headers)
        table.append(self.LINE_DIVISION_CHAR * line_division_size)
        for linex in lines:
            table.append(linex)

        if self.summary != '':
            table.append('\n**' + self.summary + ' [' + str(n_lines) + ']')

        self.table = table

        return table

    def print_table(self):
        '''Re-assembles the table and prints it, prints the table.'''

        table = self.assemble_table()
        for i in table:
            print(i)

    def _get_rows_size(self, headers_calc, rows_calc):
        '''
        Joins all values in one list and gets the maximum size, of all
        values per row.
        '''

        rows_size = []
        for i in enumerate(headers_calc):
            try:
                rows_calc[i[0]].append(headers_calc[i[0]])
                rows_size.append(len(max(rows_calc[i[0]], key=len)))
                rows_calc[i[0]].remove(headers_calc[i[0]])
            except IndexError:
                raise RbkcliException.DynaTableError('Incorrect number of '
                                                     'rows provided')

        return rows_size


class RbkcliJsonOps():
    """Manipulates json data in crazy ways."""
    def __init__(self, logger, json_data=[]):
        """Initialize the json operation."""
        self.logger = logger
        self.json_data = json_data
        self._jsonfy()

    def _jsonfy(self):
        """."""
        if (not isinstance(self.json_data, dict) and
                not isinstance(self.json_data, list)):
            self.json_data = json.loads(self.json_data)

    def simple_dict_natural(self, simple_dict={}):
        """Convert simple dictionary into natural values."""
        if simple_dict == {}:
            simple_dict = self.json_data

        result = []
        for keys, values in simple_dict.items():
            result.append('%s=%s' % (str(keys), str(values)))

        return ','.join(result)

    def natural_simple_dictstr(self, natural_str):
        """Convert natural values into simple dictionary."""
        simple_dictstr = []

        if isinstance(natural_str, list):
            natural_str = natural_str[0]
        natural_str = natural_str.split(',')
        #print(natural_str)
        for item in natural_str:
            try:
                #print(item)
                #new = item.split('=')
                #print(new)
                key, value = item.split('=')
                simple_dictstr.append('"%s": "%s"' % (key, value))
            except ValueError as e:
                raise RbkcliException.ToolsError('jsops error: ' + str(e) + '\n')
            
        #print(simple_dictstr)

        return str('{%s}' % ', '.join(simple_dictstr))

    def simple_dict_table(self, simple_dict={}, headers=[], summary=''):
        """Convert simple dictionary to table format."""

        # Declare variables to create table.
        body = {}
        f_body = []

        # If header is not passed, get the first dictionary keys as headers.
        if headers == []:
            for key in simple_dict[0].items():
                headers.append(key[0])
            headers.sort()

        # By the provided ordered headers create the final body list of lists.
        for i in enumerate(headers):
            body[i[0]] = []
            for dicio in simple_dict:
                body[i[0]].append(dicio[i[1]])
            f_body.append(body[i[0]])

        # Pass headers, body, summary and summon the table.
        my_table = DynaTable(headers,
                             f_body,
                             summary=summary,
                             ROW_DIVISION_CHAR="|",
                             LINE_DIVISION_CHAR="=")
        table = my_table.assemble_table()

        return table

    def resolve_ref(self, definitions, json_data):
        """Intantiate ResolveRef class and iterate it."""

        resolve_inst = ResolveRef(definitions, json_data)
        return resolve_inst.iterit()

    def pretty_print(self, json_data):
        """Intantiate PrettyPrint class and iterate it."""

        pprint_inst = PrettyPrint(json_data=json_data)
        return pprint_inst.iterit()


class JsonIteration():

    """Manipulates json data in crazy ways."""
    def __init__(self, definitions=[], json_data=[]):
        """Initialize the json operation."""
        self.json_data = json_data
        self.definitions = definitions
        self.counter = -2
        self.modifier = 2

    def iterit(self):
        """
        Runs a customize iteration through json data / nested dictionaries.
        """

        return self._iteration_context(self.definitions, self.json_data)

    def _iteration_context(self, definitions, json_data):
        """Allow customization of iteration context."""

        del definitions

        return self._iterate_json(json_data)

    def _iterate_json(self, json_data):
        """Iterate the json data provided."""
        new_dict = json_data
        if isinstance(json_data, dict):
            json_data = self._before_iterate_dict(json_data)
            new_dict = self._iterate_dict(json_data)
            json_data = self._after_iterate_dict(json_data)
        elif isinstance(json_data, list):
            json_data = self._before_iterate_list(json_data)
            new_dict = self._iterate_list(json_data)
            json_data = self._after_iterate_list(json_data)
        return new_dict

    def _before_iterate_dict(self, json_data):
        """Allow customization before iterating dict."""
        return json_data

    def _iterate_dict(self, json_data):
        """Iterate dictionary found in json data."""
        new_dict = copy.deepcopy(json_data)
        for keys, values in json_data.items():
            del new_dict[keys]
            keys, values = self._action_dict(keys, values, json_data)
            new_dict[keys] = values
        return new_dict

    def _action_dict(self, keys, values, json_data):
        """Allow customization of action with dict found."""

        # Deleting variable to avoid linting issues.
        del json_data
        return keys, values

    def _after_iterate_dict(self, json_data):
        """Allow customization after iterating dict."""
        return json_data

    def _before_iterate_list(self, json_data):
        """Allow customization before iterating list."""
        return json_data

    def _iterate_list(self, json_data):
        """Iterate list found in json data."""
        new_dict = []
        for line in json_data:
            new_dict.append(self._action_list(line, json_data))
        return new_dict

    def _action_list(self, line, json_data):
        """Allow customization of action with list found."""

        # Deleting variable to avoid linting issues.
        del json_data
        return line

    def _after_iterate_list(self, json_data):
        """Allow customization after iterating list."""
        return json_data


class PrettyPrint(JsonIteration):
    """."""

    def _iteration_context(self, definitions, json_data):
        """."""
        self.counter = -2
        self.modifier = 2
        self.output = []
        self._iterate_json(json_data)
        self.output_str = '\n'.join(self.output)
        return self.output_str
        

    def _action_dict(self, keys, values, json_data):
        """."""
        self.counter = self.counter + self.modifier

        #if isinstance(values, unicode):
        if isinstance(values, dict):
            #print('' + str(' ' * self.counter) + keys + ':')
            self.output.append('' + str(' ' * self.counter) + keys + ':')
            ('' + str(' ' * self.counter) + keys + ':')
            values = self._iterate_json(values)
        elif isinstance(values, list):
            #print('' + str(' ' * self.counter) + keys + ':')
            self.output.append('' + str(' ' * self.counter) + keys + ':')
            values = self._iterate_json(values)
        else:
            #print(str(' ' * self.counter) + str(keys) + ': ' + str(values))
            self.output.append(str(' ' * self.counter) + str(keys) + ': ' + str(values))
        self.counter = self.counter - self.modifier
        return keys, values

    def _action_list(self, line, json_data):
        """."""
        self.counter = self.counter + self.modifier
        #if isinstance(values, unicode):
        
        if isinstance(line, dict):
            line = self._iterate_json(line)
            line = self._before_iterate_list(line)
        elif isinstance(line, list):
            line = self._iterate_json(line)
            line = self._before_iterate_list(line)
        else:
            #print(str(' ' * self.counter) + str(line))
            self.output.append(str(' ' * self.counter) + str(line))

        self.counter = self.counter - self.modifier
        return line

    def _before_iterate_list(self, json_data):
        """."""
        #print(str(' ' * self.counter) + '----')
        return json_data

    def _after_iterate_list(self, json_data):
        """."""
        #print(str(' ' * self.counter) + '----')
        return json_data


class ResolveRef(JsonIteration):
    """
    Resolve references that are present in swagger file
    documentaion for Rubrik APIS.
    """

    def _action_dict(self, keys, values, json_data):
        """."""
        definitions = self.definitions
        if keys == "$ref":
            ref_keys = self._convert_ref_to_keys(values)
            for nks in ref_keys:
                definitions = definitions[nks]
            keys = ref_keys[-1]
            values = self._iterate_json(definitions)
        else:
            values = self._iterate_json(values)
        return keys, values

    def _action_list(self, line, json_data):
        """."""

        return self._iterate_json(line)

    def _convert_ref_to_keys(self, values):
        """Convert reference str to key to be resolved."""

        ref_keys = values.replace('#', '')
        ref_keys = ref_keys.replace('/definitions/', '')
        if '/' in ref_keys:
            return ref_keys.strip().split('/')

        return [ref_keys]


class MapResponseDoc(JsonIteration):
    """
    Create a reference of json structure and nested keys.

    It creates the same metadata map as MapJson, but reading from the documen_
    ted response from swagger.
    This map is the baseline used to validate available fields to selct for 
    each api response.
    Its very relevant to Rbkcli once it provides the capability to perform 
    relevant selections as well as autocomplete for the fields available.
    """

    def _iteration_context(self, definitions, json_data):
        """Define the context to use during iteration."""
        self.cursor = ''
        
        # Create dictionary to save all maps and make it accessible.
        self.map = DotDict({})
        self.map.full = []
        self.data_tag = False
        
        ## Fix by unifying variables and removing redundant
        self.level = 0

        # Json Keys that will be ignored while creating the map.
        # the following keys are a sort of metadata presented by the docu
        # mentation, so we use them to accuratly build a valid representation
        # of any response.
        self.excluded_fields = ['properties',
                                'items',
                                'allOf',
                                'data',
                                'hasMore',
                                'total']
        self.exclude_properties = ['type',
                                   'format',
                                   'description',
                                   'required',
                                   'enum']

        # get the schema of the response documentation only.
        try:
            json_dict = json_data['doc']['responses']['200']['schema']
        except KeyError: 
            json_dict = {}
        # Translate datatypes from documentation to python json module.
        self.type_dict = {
            'string': 'str',
            'boolean': 'bool',
            'integer': 'int',
            'empty': 'dict',
            'number': 'number',
            'array': 'list'
        }
        
        # Iterate json data creating the map
        result = self._iterate_json(json_dict)

        # Create map variations from metadata gathered
        self._gen_all_maps()

        # Return the map structure.
        return result

    def _action_dict(self, keys, values, json_data):
        """Action taken when json data is identified as dictionary."""
        
        if keys not in self.excluded_fields and not keys[0].isupper(): 
            if keys not in self.exclude_properties:
                key_str = self._appender(keys, values)
                values = self._verifier(values)
                self._remover(key_str)
            else:
                values = self._verifier(values)
        # Treating special case, which we might remove data from output.
        ## Will need further changes to allow configuration option.
        ## FIX this test
        #elif keys == 'data' or keys == 'items' :
        elif keys == 'data':
            self.data_tag = True
            self.level = self.level + 1
            values = self._verifier(values)   
            self.level = self.level - 1
        # Creating a safe check for the key levels of jsons that has both data and items.
        elif keys == 'items' and not self.data_tag:
            #self.data_tag = True
            self.level = self.level + 1
            values = self._verifier(values)   
            self.level = self.level - 1
        else:
            values = self._verifier(values)

        return keys, values

    def _action_list(self, line, json_data):
        """Action taken when json data is identified as list."""
        return self._verifier(line)

    def _appender(self, keys, values):
        """Treat and append json key metadata to cursor."""

        self.level = self.level + 1
        try:
            objt_type = values['type']
        except:
            objt_type = 'empty'

        objt_type = self.type_dict[objt_type]
        key_str = '[%s#%s#%s]' % (keys, str(self.level), objt_type)

        self.cursor = self.cursor + key_str
        self.map.full.append(self.cursor)

        return key_str

    def _verifier(self, values):
        """Verify data type from received value."""
        # Iterate possible nested keys.
        if (not isinstance(values, str) or
            not isinstance(values, bool) or
            not isinstance(values, int)):
            values = self._iterate_json(values)

        return values

    def _remover(self, key_str):
        """Remove json key metadata from cursor."""
        self.cursor = self.cursor.replace(key_str, '')
        self.level = self.level - 1

    def _gen_all_maps(self):
        """Load map var with uniq and sorted map_list ."""
        self.map.full = list(set(self.map.full))
        self.map.full.sort()
        self.gen_simple_keys()

    def gen_simple_keys(self):
        """Split the keys from full map into categories."""
        nested_keys = copy.copy(self.map.full)
        all_simple_keys = []

        for key in self.map.full:
            if '][' not in key and key in nested_keys:
                nested_keys.remove(key)
                all_simple_keys.append(key)

        simple_keys = copy.copy(all_simple_keys)
        for key in all_simple_keys:    
            for key_ in nested_keys:
                if key_.startswith(key) and key in simple_keys:
                    simple_keys.remove(key)

        self.map.simple_keys = simple_keys
        self.map.nested_keys = nested_keys
    
    def mapit(self):
        """Return the map dict."""
        # Try and get any value assigned to map, if it does not exist
        # reiter the json data to get it.
        try:
            map_it = self.map
            del map_it
        except:
            self.iterit()

        # Returns map only.
        return self.map


class MapSelect(JsonIteration):

    # Need to add the fields requested to this function, in that way
    # during the iteration we can match the field requested with the lopped ones.

    ## Fix by unifying this class with MapJson, the current class performs
    # further actions than just MAP, but it also maps, so adding options
    # during the iteration should fix that.

    def _iteration_context(self, definitions, json_data):
        """."""
        # Assign definitions to instance var.
        if definitions == []:
            definitions = {}
        self.definitions = definitions

        # Assign flag for returning the selected data.
        self.returning = True

        # Create the necessary var for map validated selection.
        self.cursor = ''
        self.level = 0
        # Create dictionary to save all maps and make it accessible.
        self.map = DotDict({})
        self.map.full = []

        # Dictionary with selected keys.
        self.selected = {}
        ### TEST
        self.unselected = {}

        for key, value in definitions.items():
            self.selected[key] = 'N/A'
            self.unselected[key] = ''

        # Iterate provided json data.
        result = self._iterate_json(json_data)

        # Once the iteration is based on the metadata_key that is matched
        # then, the ones that are not matched are never treated, so:
        # Created the unselected dictionary that stores the keys that were never analyzed.
        # If after the iteration, there are unselected fields that are
        # supposed to be filtered, then result shoud not be returned.
        # Pratical meaning here is, if a filter/selection was ordered but the 
        # field which we are filtering does not exist in the json at hand, 
        # the code will interprete it as a miss match and not add it to the list of results.
        for key in self.unselected:
            #if definitions[key]['filter_eq'] != '':
            if (definitions[key]['filter_eq'] != '' or 
                 definitions[key]['filter_aprox'] != '' or
                 definitions[key]['filter_not'] != '' or
                 definitions[key]['filter_not_aprox'] != ''):
                self.returning = False

        # From full map create simple keys map.
        self._gen_all_maps()

        # Use the flag to determine the return.
        if self.returning:
            return self.selected
        return {}

    def _select_key(self, found_metadata, found_value):
        """Get the value of the key obeying condition."""
        # Only load value if definitions has been passed.
        for key, value in self.definitions.items():
            #print(found_metadata)
            #print(value['dictKey'])
            # Match key metadata with passed metadata.
            if value['dictKey'] == found_metadata:
                # In case a filter is specified take action.
                if value['filter_eq'] != '': 
                    if value['filter_eq'] == str(found_value):
                        self.selected[key] = found_value
                        del self.unselected[key]
                    else:
                        # If filter is not met do not return anything.
                        self.returning = False
                elif value['filter_aprox'] != '': 
                    if value['filter_aprox'] in str(found_value):
                        self.selected[key] = found_value
                        del self.unselected[key]
                    else:
                        # If filter is not met do not return anything.
                        self.returning = False

                elif value['filter_not_aprox'] != '':
                    if value['filter_not_aprox'] not in str(found_value):
                        self.selected[key] = found_value
                        del self.unselected[key]
                    else:
                        # If filter is not met do not return anything.
                        self.returning = False
                elif value['filter_not'] != '':
                    if value['filter_not'] != str(found_value):
                        self.selected[key] = found_value
                        del self.unselected[key]
                    else:
                        # If filter is not met do not return anything.
                        self.returning = False
                else:
                    # If no filter is specified assign the whole value.
                    self.selected[key] = found_value
                    del self.unselected[key]


    def _action_dict(self, keys, values, json_data):
        """Action taken when json data is identified as dictionary."""
        # Accumulate nesting level.
        self.level = self.level + 1
        
        # Generate key metadata and select the filtered key.
        metadata = self._gen_metadata(keys, values)
        #self._select_key(metadata, values)

        # Generate cursor and append it to the map.
        self.cursor = self.cursor + metadata
        ## Test
        #self._select_key(self.cursor, values)
        
        ###BAD TEST FOR SERIALIZED JSON in values
        if isinstance(values, str):
            try:
                values = json.loads(values)
            except:
                pass
        self._select_key(self.cursor, values)
        self.map.full.append(self.cursor)
        
        # Iterate possible nested keys.
        if (not isinstance(values, str) or
            not isinstance(values, bool) or
            not isinstance(values, int)):
            values = self._iterate_json(values)

        # Removing key metada from cursor.
        self.cursor = self.cursor.replace(metadata, '')
        self.level = self.level - 1

        return keys, values

    def _action_list(self, line, json_data):
        """Action taken when json data is identified as list."""
        # Accumulate nesting level.
        self.level = self.level + 1
        
        ###BAD TEST
        if isinstance(line, str):
            try:
                line = json.loads(line)
            except:
                pass

        # Iterate possible nested keys.
        if (not isinstance(line, str) or
            not isinstance(line, bool) or
            not isinstance(line, int)):
            line = self._iterate_json(line)
        
        # Removing nesting level.
        self.level = self.level - 1
        return line

    def _gen_metadata(self, keys, values):
        """Generate json key metadata."""
        objt_type = str(type(values))
        objt_type = objt_type.split('\'')
        objt_type = objt_type[-2]
        return '[%s#%s#%s]' % (keys, str(self.level), objt_type)

    def _gen_all_maps(self):
        """Load map var with uniq and sorted map_list ."""
        self.map.full = list(set(self.map.full))
        self.map.full.sort()
        self._gen_simple_keys()

    def _gen_simple_keys(self):
        """Split the keys from full map into categories."""
        # Copy original map to facilitate iteration
        nested_keys = copy.copy(self.map.full)
        all_simple_keys = []

        # Iterate over full map appending all the level 1 keys.
        for key in self.map.full:
            if '][' not in key and key in nested_keys:
                nested_keys.remove(key)
                all_simple_keys.append(key)

        # Iterate over all level 1 keys to remove the nested ones
        simple_keys = copy.copy(all_simple_keys)
        for key in all_simple_keys:    
            for key_ in nested_keys:
                if key_.startswith(key) and key in simple_keys:
                    simple_keys.remove(key)

        # Make the key variations part of map.
        self.map.simple_keys = simple_keys
        self.map.nested_keys = nested_keys

    def key_metadata_key(self, metadata_map):
        """Convert metadata map created to list of keys."""
        str_key_lst = []
        for metadata_key in metadata_map:
            str_key = ''
            metadata_key = metadata_key.split('[')
            metadata_key.pop(0)
            for key in metadata_key:
                key = key.split('#')
                key = key[0]
                str_key = str_key + '[' + key + ']'
            str_key_lst.append(str_key)
        return str_key_lst

    def mapit(self):
        """Return the map dict."""
        # Try and get any value assigned to map, if it does not exist, reiter.
        try:
            map_it = self.map
            del map_it
        except Exception as e:
            self.iterit()

        # Returns map only.
        return self.map

