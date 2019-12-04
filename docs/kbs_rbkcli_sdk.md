# rbkcli SDK

The **rbkcli SDK** allows you to instantiate objects from RbkCli class to create independent parallel connections to different clusters or nodes. In other words it allows for a higher level of automation leveraging all **rbkcli** capabilities.

## Usage
To use rbkcli as an SDK, you can simply import the class **RbkCli**.
The following example is an simple way of creating your own custom file to call rbkcli commands:
```python
"""My rbkcli"""

import sys

from rbkcli import RbkCli

# Get arguments passed.
arg_list = sys.argv[1:]

# Instantiate rbkcli as object.
# Gets authentication from default methods.
rbk_cli = RbkCli()

# Call execute method.
output = rbk_cli.execute(arg_list)

# Print the output to user.
print(output)
```

You can also provide authentication during instantiation and perform multiple instantiation in the same script. For some advanced cases please visit Cases.

## Cases
Following are some real use cases to elucidate the SDK usage:
 - [Multi target script](multi_target_script.md)
 - [Automate Managed Volumes with rbkcli](KB0018.md)  