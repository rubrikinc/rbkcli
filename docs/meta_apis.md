# Meta APIS
---
## Definition
The Meta APIs are hard coded APIs into rbkcli. Those have the same documentation, methods and parameters as any RESTful APIs. The version of the Meta APIs is **"rbkcli"**, therefore when listing all available commands you can filter them by using the following command:
```
$  rbkcli commands --filter version=rbkcli -T
 version | endpoint       | method | summary
==================================================================================
 rbkcli  | cmdlet profile | get    | List cmdlet's profiles
 rbkcli  | cmdlet profile | post   | Create cmdlet profile.
 rbkcli  | cmdlet sync    | post   | Apply cmdlets changes to target profile.
 rbkcli  | cmdlet         | delete | Remove cmdlet.
 rbkcli  | cmdlet         | get    | List available cmdlets.
 rbkcli  | cmdlet         | post   | Add new cmdlet to rbkcli
 rbkcli  | commands       | get    | List available commands
 rbkcli  | jsonfy         | get    | Loads provided json file.
 rbkcli  | script sync    | post   | Example of method created internally.
 rbkcli  | script         | get    | List scripts available to be used in rbkcli.

**Total amount of objects [10]

```

They are, as a mater of fact, features designed to complement and facilitate the usage of Rubrik APIs. Whenever new versions of rbkcli are developped, with new features, it is in under this API version where the new features should land and be called from.

 - [/rbkcli/commands](rbkcli_commands.md)
 - [/rbkcli/jsonfy](rbkcli_jsonfy.md)
 - [/rbkcli/cmdlet](rbkcli_cmdlet.md)
 - [/rbkcli/cmdlet/profile](rbkcli_cmdlet_profile.md)
 - [/rbkcli/cmdlet/sync](rbkcli_cmdlet_sync.md)
 - [/rbkcli/script](rbkcli_script.md)


[Back to [Summary](SUMMARY.md)]