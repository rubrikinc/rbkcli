# Usage
## Help message
When an user types rbkcli -h or --help, it returns the following message:  
* -h/--help
    ```
    usage:
    $ rbkcli <api_endpoint> <options>
    $ rbkcli cluster me --select id
    
    > [rbkcli] Easy calls to Rubrik APIs from CLI.
    
    ==> Positional arguments <==:
     <api_endpoint>        The API endpoint to be requested, required argument
    
    ==> Optional arguments <==:
      -h, --help            show this help message and exit
      -m <method>, --method <method>
                            Method to request Rubrik API
      -v <version>, --version <version>
                            Explicit version of the Endpoint requested.
      -q <query>, --query <query>
                            In path query to customize API request.
      -p <parameter>, --parameter <parameter>
                            Parameter passed to the API request, json.
      -i, --info            Flag to return information on the Provided API
                            endpoint.
      -d, --documentation   Documentation related to the provided endpoint and
                            method.
      -s <select>, --select <select>
                            Select the json fields from the output.
      -f <filter>, --filter <filter>
                            Filter the value of the provided fields from the json
                            results.
      -c <context>, --context <context>
                            Cut the json output into the provided field of
                            context.
      -l <key> <new_endpoint>, --loop <key> <new_endpoint>
                            Loop resulting json values into another API request.
      -T, --table           Convert json output into Table output, if possible.
      -L, --list            Convert json output into list output, if possible.
      -P, --pretty_print    Convert json output into list output, if possible.
    
    For all available commands run: $ rbkcli commands -q <cmd_name>
    ```

## Arguments description
The arguments available afect the command execution in 2 different ways and therefore their explanation will be also split into the following groups:
- API endpoints to call.
- JSON output customization.
 
### API Endpoints arguments
The arguments described following are all related to calling the API endpoint desired with the appropriate data being provided.
- **<api_endpoint>:** This is a required argument and as such no “-” parameters are needed. Provide the API endpoint which you want to call, it accepts the endpoint in a couple of different ways, but it is only autocompletable when using in the following form:
    1. *autocompletable format:* provide the endpoint with or without its version, separated by spaces.   Example:  
        ```
        $ rbkcli cluster me
        ```
        ```
        $ rbkcli v1 cluster me
        ```

    2. *other accepted formats:* provide the endpoint with or without its version, separated by slashes (“/”) as if it was the endpoint path.The result will be the same as the ones above, but autocomplete is not available.
    Examples:
        ```
        $ rbkcli /cluster/me
        ```
        ```
        $ rbkcli /v1/cluster/me
        ```

- **-v/--version:** This is an optional argument. Provide the API version which the endpoint belongs to. You can provide the version in the command line, implicit as the first argument. Given the large number of available commands, the implicit method can get confusing, then you can explicitly define the version:
    1. *implicit version:* When user don’t provides version or provide it with the endpoint.
    Example:
        ```
        $ rbkcli cluster me
        ```
        ```
        $ rbkcli /v1/cluster/me
        ```
        
    2. *explicit version:* When user provide the version with appropriate argument “-v/--version”.
    Example:
        ```
        $ rbkcli cluster me -v v1
        ```
        ```
        $ rbkcli /cluster/me --version v1
        ```

 - **-m/--method:** This is an optional argument. The default method used by rbkcli is “get”, so as a matter of fact, in order to call an API, the method is required, but due the get operations being the most common and secure, it was decided to set it as the default. If the method of operation/endpoint that you want to call is different than “get” you need to explicitly request it:
    1. *implicit method:* When user does not provide method argument and it assumes “get”.
    Example:
        ```
        $ rbkcli cluster me
        ```

    2. *explicit method:* When user provide the method with appropriate argument “-m/--method”.
    Example:
        ```
        $ rbkcli cluster me -v v1 -m get
        ```
        ```
        $ rbkcli session --version v1 --method post
        ```

 - **-q/--query:** This is an optional argument. This argument depends completely on how the API endpoint was designed and whether or not it accepts queries. The queries passed explicitly will be later concatenated in path with “?” after the endpoint. It can also be passed in line with the endpoint:
    1. *inline query:* When provided with the endpoint altogether, similar to curl usability. 
    Example:
        ```
        $ rbkcli /v1/vmware/host?primary_cluster_id=<id>
        ```

    2. *explicit query:* When user provide the query with appropriate argument “-q/--query”.
    Example:
        ```
        $ rbkcli vmware host -q primary_cluster_id=<id>
        ```

 - **-p/--parameter:**  This is an optional argument. This argument depends completely on how the API endpoint was designed and whether or not it accepts/requires parameters to run successfully. Parameters are usually required in methods that causes a modification in ab object (post, delete, etc...). The parameters have to be passed explicitly, but they are accepted in 2 formats: json and natural keys assignment.
    1. *natural key assignment:* When the parameters required are simple, not a nested json, they can be passed like the query parameters. Rbkcli has a module that will translate that into the json argument needed.
    Example:
        ```
        $ rbkcli user -m post -p username=test.cli,password=test.cl
        ```

    2. *json parameter:* When the parameters required are complex and nested json, they have to be passed as a json string.
    Example:
        ```
        $ rbkcli cmdlet -m post -p '{"name": "vms archive snaps", "param": "locationName", "command": ["rbkcli archive location --filter name~<locationName> --loop id,name \"vmware vm --loop id vmware/vm/{id} -c snapshots -f archivalLocationIds~{{id}}\" -s id,date,vmName"], "profile": "DemoTest-cmdlets.json"}'
        ```

 - **-i/--info:** This is an optional argument and it’s a True/False flag. If this argument is used then the API endpoint will not be called, instead a small summary of the available information on the endpoint will be returned. This will also list the available queries and parameters for a specific endpoint with a short explanation.
    1. *endpoint information:* When user need to confirm what it is being called and what is accepted in the call.
    Example:
        ```
        $ rbkcli cluster me --info
        Description: [Retrieve public information about the Rubrik cluster]
           Endpoint: [/v1/cluster/{id}]
             Method: [get]
         Parameters: [1]
                     -id
                       Description: ID of the Rubrik cluster or *me* for self..
                       Additional info: This parameter is REQUIRED to run and should be provided in the path as a string.
        ```

 - **-d/--documentation:** This is an optional argument and it’s a True/False flag. If this argument is used then the API endpoint will not be called, instead all of the available information on the endpoint will be returned. This will also list the available queries and parameters for a specific endpoint with explanation and definition.
    1. *endpoint documentation:* When users needs to verify what are all specification of an API endpoint, what are the required parameters and expected response schema.
    Example:
        ```
        $ rbkcli cluster me --documentation
        ```
        ```
        $ rbkcli /v1/cluster/me -d
        ```

### Json output customization arguments
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
        
## Plus
With the exception of the arguments that convert the output into a different format, all arguments can be used multiple times in series, where you can continually modify the output until you get the desired output.
That is covered in advanced usage documentation:
* [Advanced usage](advanced_usage.md)
