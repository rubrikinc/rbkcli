# Json output customization arguments
The following arguments are all related to customization of the JSON output received from APIs, as well as using the output to create advanced workflows. This arguments can be used multiple times in the same command line and it will cause a modification to the received output. It works in a similar manner to the pipeline on Linux bash. Because of the nature of the data needed by this argumetns, the values provided have it own notation. The notaion rbkcli uses is called *natural key assignment* (it was mentioned on [**-p/--parameters**] section), lets take a look at its characteristics before describing its usage.

- **natural key assignment**: Notation in which you can define keys and values (as in  [JSON](https://www.w3schools.com/js/js_json_objects.asp) or [Python dictionary](https://realpython.com/python-dicts/) keys and values) in a simple manner. Currently the arguments that make usage of that are: *[-q/--query]*, *[-p/--parameter]*, *[-s/--select]*, *[-f/--filter]*, *[-c/--context]*. The bash argument is one long string which is later parsed by rbkcli into the needed format. Following are its usages:
    1. *[-q/--query],[-p/--parameter]*: To get usable and required keys for queries and parameters, run the command with *[-i/--info]* or *[-d/--documentation]* flag. Query and Parameter only accepts the following format, because the data will be input for the API: 
        ```
        <key1>=<value>,<key2>=<value>
        ```
        Example:
        ```
        $ rbkcli event --query limit=5,status=Failure
        ```
        ```
        $ rbkcli vmware config set_esx_subnets -m patch --parameter "esxSubnets=10.10.10.0/24"
        ```
    
    3. *[-s/--select],[-f/--filter]*: To get usable keys for selection and filters, run the command with *[-s/--select]* or *[-f/--filter]* followed by a question mark ("?"). Select and Filter accepts indirect assignments, because we are choosing existing data to be displayed, giving us a range of different values available:
        * When you want to select results that contain a key with an exact value, use:
        ```
        <key1>=<value>
        ```
        Example:
        ```
        $ rbkcli commands --select method=get
        ```

        * When you want to select results that contain a key with an aproximated value (or key that contains the string), use:
        ```
        <key1>~<value>
        ```
        Example:
        ```
        $ rbkcli commands --select endpoint~vmware
        ```
        
        * When you want to select results that contain a key without an exact value, use:
        ```
        <key1>!=<value>
        ```
        Example:
        ```
        $ rbkcli commands --select method!=delete
        ```
        Obs.: Because bash interpretes exclamation mark as a special character, users should escape that character:
        ```
        $ rbkcli commands --select method\!=delete
        ```
        
        * When you want to select results that contain a key without an aproximated value (or key that does not contains the string), use:
        ```
        <key1>~<value>
        ```
        Example:
        ```
        $ rbkcli commands --select endpoint!~config
        ```
        Obs.: Because bash interpretes exclamation mark as a special character, users should escape that character:
        ```
        $ rbkcli commands --select endpoint\!~config
        ```

- **-s/--select:**: This is an optional argument used to select only specific keys from a Json output, customizing the output as desired. With this argument you can, get simple keys (not nested), get all keys in json output, select specific keys as well as select keys with condition.
    1. To get the simple keys in json output, use the following:
    Example 1:
        ```
        $ rbkcli commands -s ?
        [endpoint]
        [method]
        [summary]
        [version]
        ```
        Example 2:
        ```
        $ rbkcli cluster me -s ?
        [acceptedEulaVersion]
        [apiVersion]
        [id]
        [latestEulaVersion]
        [name]
        [version]
        ```
        
    2. To get all the available keys in json output, use the following:
        ```
        $ rbkcli cluster me -s ?MAP
        [acceptedEulaVersion]
        [apiVersion]
        [geolocation]
        [geolocation][address]
        [id]
        [latestEulaVersion]
        [name]
        [timezone]
        [timezone][timezone]
        [version]
        ```
    3. To select specific simple keys and nested keys, use the following:
        Example 1: Selecting simple key and nested parent key:
        ```
        $ rbkcli cluster me -s [id],[timezone]
        {
          "id": "a8cd537d-e274-46d8-871e-f80ac47c264c",
          "timezone": {
            "timezone": "Europe/London"
          }
        } 
        ```
        Example 2: Selecting simple key and nested child key:
        ```
        $ rbkcli cluster me -s [id],[timezone][timezone]
        {
          "id": "a8cd537d-e274-46d8-871e-f80ac47c264c",
          "timezone_timezone": "Europe/London"
        }
        ```
        Obs.: You can see that the nested child key becomes a simple key, accumulating the parent keys name.
        
    4. To select keys with condition to its value, use the following:
        Example 1:
        ```
        $ rbkcli commands --select version=v2,endpoint,method\!~p
        [
          {
            "version": "v2",
            "endpoint": "sla_domain {id}",
            "method": "delete"
          },
          {
            "version": "v2",
            "endpoint": "sla_domain {id}",
            "method": "get"
          },
          {
            "version": "v2",
            "endpoint": "sla_domain",
            "method": "get"
          }
        ]
        ```
        Explanation.: The above command selects the key "version" only if its value is exactly "v2", selects the key "endpoint" with no condition and selects the key "method" only if its value does not contain the letter p.
        
- **-f/--filter:**: This is an optional argument used to filter results in which specific keys from Json output has specific values, customizing the output as desired. With this argument you can, get simple keys (not nested), get all keys in json output, filter objects from a returned list, if it does not meet specified values.
    1. To get the simple keys in json output, use the following:
    Example 1:
        ```
        $ rbkcli commands --filter ?
        [endpoint]
        [method]
        [summary]
        [version]
        ```
        Example 2:
        ```
        $ rbkcli cluster me -f ?
        [acceptedEulaVersion]
        [apiVersion]
        [id]
        [latestEulaVersion]
        [name]
        [version]
        ```
        
    2. To get all the available keys in json output, use the following:
        ```
        $ rbkcli cluster me -f ?MAP
        [acceptedEulaVersion]
        [apiVersion]
        [geolocation]
        [geolocation][address]
        [id]
        [latestEulaVersion]
        [name]
        [timezone]
        [timezone][timezone]
        [version]
        ```
    3. To filter results based on key values, use the following:
        ```
        $ rbkcli commands --filter version=v2,method\!~p
        [
          {
            "version": "v2",
            "endpoint": "sla_domain {id}",
            "method": "delete",
            "summary": "Remove SLA Domain"
          },
          {
            "version": "v2",
            "endpoint": "sla_domain {id}",
            "method": "get",
            "summary": "Get SLA Domain details"
          },
          {
            "version": "v2",
            "endpoint": "sla_domain",
            "method": "get",
            "summary": "Get list of SLA Domains"
          }
        ]
        ```
        Obs.: Even though we have only specified 2 keys in the filter, all keys are returned and the objects that does not match that filter are discarded.
    
- **-c/--context:**: This is an optional argument used to display only the value of a specified key. It changes the context of the output from general, to the specified key, it is specially useful when dealing with nested keys and conplex outputs or creating simple list of data. It also accepts conditions to generate the list. With this argument you can, get simple keys (not nested), get all keys in json output and get the keys values alone.
    1. To get the simple keys in json output, use the following:
    Example 1:
        ```
        $ rbkcli commands --context ?
        [endpoint]
        [method]
        [summary]
        [version]
        ```
        Example 2:
        ```
        $ rbkcli cluster me -c ?
        [acceptedEulaVersion]
        [apiVersion]
        [id]
        [latestEulaVersion]
        [name]
        [version]
        ```
        
    2. To get all the available keys in json output, use the following:
        ```
        $ rbkcli cluster me -c ?MAP
        [acceptedEulaVersion]
        [apiVersion]
        [geolocation]
        [geolocation][address]
        [id]
        [latestEulaVersion]
        [name]
        [timezone]
        [timezone][timezone]
        [version]
        ```
        
    3. To change the context to the value of the key, use the following:
        Example 1: Change context of simple keys.
        ```
        $ rbkcli cluster  me -c name,version
        [
          "ORK-Support",
          "5.0.0-p2-1122"
        ]
        ```
        
        Example 2: Change context of nested keys.
        ```
        $ rbkcli cluster  me -c geolocation,timezone
        [
          {
            "address": "Cork, Ireland"
          },
          {
            "timezone": "Europe/London"
          }
        ]
        ```
- **-l/--loop:** This is an optional argument used to select a key from an output or list of outputs and use it to call other rbkcli command, replacing a specified string by the selected key. Loop takes 2 arguments <key> and <loop_command>. The key(s) selected are then merged to the resulting output, with the prefix "loop_" added to it. 
    1. To loop keys to other commands, use the following:
    Example 1: Dummy example to facilitate understanding the loop concept.
        ```
        $ rbkcli cluster me -l id cluster/{id}
        [
          {
            "id": "a8cd537d-e274-46d8-871e-f80ac47c264c",
            "version": "5.0.0-p2-1122",
            "apiVersion": "1",
            "name": "ORK-Support",
            "timezone": {
              "timezone": "Europe/London"
            },
            "acceptedEulaVersion": "1.1",
            "latestEulaVersion": "1.1",
            "loop_id": "a8cd537d-e274-46d8-871e-f80ac47c264c"
          }
        ]
        ```
        Explannation: rbkcli ran ```cluster me``` command and from it, took the id key, which was used while calling the command ```cluster/{id}```. The Loop replaces the selected id by the "{id}" string provided and performs a call back to run the new api ```cluster/a8cd537d-e274-46d8-871e-f80ac47c264c```. Once that is done Loop merges the key used in the loop into the result, in this case being called "loop_id". We can verify this by running manually  ```cluster/a8cd537d-e274-46d8-871e-f80ac47c264c```:
        ```
        $ rbkcli cluster/a8cd537d-e274-46d8-871e-f80ac47c264c
        {
          "id": "a8cd537d-e274-46d8-871e-f80ac47c264c",
          "version": "5.0.0-p2-1122",
          "apiVersion": "1",
          "name": "ORK-Support",
          "timezone": {
            "timezone": "Europe/London"
          },
          "acceptedEulaVersion": "1.1",
          "latestEulaVersion": "1.1"
        }
        ```
        Obs.: We can see it returns the same output without the looped key.
        
- **-T/--table:** This is an optional argument and a flag used to convert the final output into a table where possible. This canno't be used with *[-L/--list]* or *[-P/--pretty_print]*. The Table argument will atempt to convert every key into a row, if the output contains multiple results with keys of same name (multiple results and all of them have an "id" key for example), then one row with that name will be created and the values for each result will be added as a line. It works best with outputs that contain multiple results and it looks nicer when it is used with *[-s/--select]* or *[-f/--filter]* .
    1. To generate a table for an output, use the following:
    Example 1
        ```
        $ rbkcli commands --filter version=v2,method\!~p  -T
         version | endpoint        | method | summary
        ==============================================================
         v2      | sla_domain {id} | delete | Remove SLA Domain
         v2      | sla_domain {id} | get    | Get SLA Domain details
         v2      | sla_domain      | get    | Get list of SLA Domains
        
        **Total amount of objects [3]
        ```
        Example 2
        ```
        $ rbkcli user -s id,username~sql,emailAddress -T
         id                                          | username | emailAddress
        =======================================================================
         User:::81714fad-e119-4275-be02-cfd47042ece3 | ak_sql   | N/A
         User:::a535058c-1a27-4410-b16a-94fec218ec5d | sqltest  | N/A
        
        **Total amount of objects [2]
        ```
    
- **-L/--list:** This is an optional argument and a flag used to convert the final output into a table with a list format where possible. This canno't be used with *[-T/--table]* or *[-P/--pretty_print]*. The Table argument will atempt to convert every key in the output into a "key" row and every value into a "value" row. It works better with outputs that have only one result returned.
     1. To generate a table with list of keys and values for an output, use the following:
        Example 1:
        ```
        $ rbkcli cluster me -L
         key                 | value
        ============================================================
         acceptedEulaVersion | 1.1
         apiVersion          | 1
         geolocation         | {'address': 'Cork, Ireland'}
         id                  | a8cd537d-e274-46d8-871e-f80ac47c264c
         latestEulaVersion   | 1.1
         name                | ORK-Support
         timezone            | {'timezone': 'Europe/London'}
         version             | 5.0.0-p2-1122
        
        **Total amount of objects [8]
        ```
- **-P/--pretty_print:** This is an optional argument and a flag used to convert the final output into a table with a list format where possible. This canno't be used with *[-T/--table]* or *[-L/--list]*. The pretty print argument will convert all json output into simple indented string output. It is usefull to get a raw list of the json output and oftenly can be combined with *[-c/--context]*.
    1. To generate a pretty print output, use the following:
        Example 1:
        ```
        $ rbkcli cluster me -P
        acceptedEulaVersion: 1.1
        apiVersion: 1
        geolocation:
          address: Cork, Ireland
        id: a8cd537d-e274-46d8-871e-f80ac47c264c
        latestEulaVersion: 1.1
        name: ORK-Support
        timezone:
          timezone: Europe/London
        version: 5.0.0-p2-1122
        ```
        Example 2:
        ```
        $ rbkcli commands --filter version=v2,method=get --context endpoint --pretty_print
        sla_domain {id}
        sla_domain
        ```
