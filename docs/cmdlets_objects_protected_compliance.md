 # /cmdlets/objects/protected/compliance
 
 ### Basic Usage
 In order to run this cmdlet you must run:
 ```
 $ rbkcli objects protected compliance
 ```
 For better visibility you can use the json table converter:
 ```
 $ rbkcli objects protected compliance --table
 ```
 
 ### Description
 
 This is a default cmdlet, which provides a list the compliance status of all objects that are or were protected, the data comes from Object Protection Summary report. It will return a json list of results with the following fields: ObjectName, ObjectState, ObjectType, SlaDomain, ComplianceStatus, Location.
 
 
 ### Technical Info Breakdown
 
 Following is the original **rbkcli** command, which this **cmdlet** translates to:
 ```
 rbkcli report -f "name=Object Protection Summary,type=Canned" -l id "jsonfy/report_table -p report_id={id},limit=9999" -s ObjectName,ObjectState,ObjectType,SlaDomain,ComplianceStatus,Location
 ```
 
 Let's start by understanding the initial command:
 ```
 rbkcli report -f "name=Object Protection Summary,type=Canned" 
 ```
 In this command we are querying for all the reports available in Rubrik system and then filtering by the name of "Object Protection Summary" and the type "Canned". 
 
 Moving to the second part of the command we have:
 ```
 --loop id "jsonfy/report_table -p report_id={id},limit=9999"
 ```
 With the result received, which is just one, we loop the "id" field into the API endpoint "/jsonfy/report_table -p report_id={id},limit=9999". 
 The "/jsonfy/report_table" is a custom script, which requests the following endpoint: "/internal/report/{id}/table" and converts that data into json list of elements.
 Effectively we are requesting a maximum limit of "9999" objects in the results, coming from that report.
 
 For the last part of of the command we have:
 ```
 --select ObjectName,ObjectState,ObjectType,SlaDomain,ComplianceStatus,Location
 ```
 From all the fields generated from the report table requested, we only select those six above, having a more concise result.
 
 ### Adding it manually
 The command line used to create a cmdlet such as this is:
 ```
 rbkcli cmdlet -m post -p '{"profile": "rbkcli","command": ["rbkcli report -f \"name=Object Protection Summary,type=Canned\" -l id \"jsonfy/report_table -p report_id={id},limit=9999\" -s ObjectName,ObjectState,ObjectType,SlaDomain,ComplianceStatus,Location"],"table_order": ["ObjectName", "ObjectState", "ObjectType", "SlaDomain", "ComplianceStatus", "Location"],"cmdlet_summary": "List the compliance status of all objects that are or were protected.","cmdlet_description": "List the compliance status of all objects that are or were protected, the data comes from Object Protection Summary report.","name": "objects protected compliance","param": "","response_description": "Returns a json list of results with the following fields: ObjectName, ObjectState, ObjectType, SlaDomain, ComplianceStatus, Location."}'
 ```
 
 The response given from rbkcli would be:
 
 ```json
  {
    "result": "Succeeded.",
    "message": "Found the following cmdlets with the provided ID(s).",
    "data": [
      {
        "cmdlet_description": "List the compliance status of all objects that are or were protected, the data comes from Object Protection Summary report.",
        "cmdlet_summary": "List the compliance status of all objects that are or were protected.",
        "command": [
          "rbkcli report -f \"name=Object Protection Summary,type=Canned\" -l id \"jsonfy/report_table -p report_id={id},limit=9999\" -s ObjectName,ObjectState,ObjectType,SlaDomain,ComplianceStatus,Location"
        ],
        "id": "6a3f27d1-bbd0-48a7-85c1-a95e4722c71f",
        "multiple_output": "segmented",
        "name": "objects protected compliance",
        "param": "",
        "profile": "rbkcli-cmdlets.json",
        "response_description": "Returns a json list of results with the following fields: ObjectName, ObjectState, ObjectType, SlaDomain, ComplianceStatus, Location.",
        "table_order": [
          "ObjectName",
          "ObjectState",
          "ObjectType",
          "SlaDomain",
          "ComplianceStatus",
          "Location"
        ]
      }
    ]
  }
 ```
 
 ### Further usage
 Additional usage for this command line could be:
 - Filtering by object compliance status, status which is equal to "NonCompliance":
 ```
 $ rbkcli objects protected compliance -f ComplianceStatus~NonCompliance -T
 ```
 - Searching for an object by SLA domain name, name which contains "Bronze":
 ```
 rbkcli objects protected compliance -f SlaDomain~Bronze -T
 ```
 - Filtering by object location, location which contains "192.168.75.53":
 ```
 $ rbkcli objects protected compliance -f Location~192.168.75.53 -T
 ```