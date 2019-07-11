# Natural key assignment

Notation in which you can define keys and values (as in  [JSON](https://www.w3schools.com/js/js_json_objects.asp) or [Python dictionary](https://realpython.com/python-dicts/) keys and values) in a simple manner. Currently the arguments that make usage of that are: *[-q/--query]*, *[-p/--parameter]*, *[-s/--select]*, *[-f/--filter]*, *[-c/--context]*. The argument provided in rbkcli command line (in bash environment) is one long string which is later parsed by rbkcli into the needed format. Following are its usages:
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

2. *[-s/--select],[-f/--filter]*: To get usable keys for selection and filters, run the command with *[-s/--select]* or *[-f/--filter]* followed by a question mark ("?"). Select and Filter accepts indirect assignments, because we are choosing existing data to be displayed, giving us a range of different values available:
    * When you want to select results that contain a key with an exact value, use:
    ```
    <key1>=<value>
    ```
    Example:
    ```
    $ rbkcli commands --select method=get
    ```

    * When you want to select results that contain a key with an approximated value (or key that contains the string), use:
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
    Obs.: Because bash interprets exclamation mark as a special character, users should escape that character:
    ```
    $ rbkcli commands --select method\!=delete
    ```
    
    * When you want to select results that contain a key without an approximated value (or key that does not contains the string), use:
    ```
    <key1>~<value>
    ```
    Example:
    ```
    $ rbkcli commands --select endpoint!~config
    ```
    Obs.: Because bash interprets exclamation mark as a special character, users should escape that character:
    ```
    $ rbkcli commands --select endpoint\!~config
    ```

[Back to [Usage](usage.md)]