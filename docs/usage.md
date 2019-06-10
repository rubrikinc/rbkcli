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
The arguments available affect the command execution in 2 different ways and therefore their explanation will be also split into the following groups:
- [API endpoints to call](api_endpoint.md)
- [JSON output customization](json_output.md)


[Back to [Summary](SUMMARY.md)]