# API Endpoints arguments
The arguments described following are all related to calling the API endpoint desired with the appropriate data being provided.
- **<api_endpoint>:** This is a required argument and as such no “-” parameters are needed. Provide the API endpoint which you want to call, it accepts the endpoint in a couple of different ways, but it is only auto-completable when using in the following form:
    1. *auto-completable format:* provide the endpoint with or without its version, separated by spaces.   Example:  
        ```
        $ rbkcli cluster me
        ```
        ```
        $ rbkcli v1 cluster me
        ```

    2. *other accepted formats:* provide the endpoint with or without its version, separated by slashes (“/”) as if it was the endpoint path.The result will be the same as the ones above, but auto-complete is not available.
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
[Back to [Usage](usage.md)]