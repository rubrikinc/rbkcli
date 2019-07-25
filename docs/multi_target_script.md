# Multi target script

This is a demonstration of a **rbkcli SDK** script.

### Scenario
For this scenario let's imagine that:
- You want to connect to multiple nodes of the same cluster, or different clusters.
- You want to enter one command and repeat it across all targets.

### What can I do?
1. Use a script such as the following, instantiate rbkcli independently per target.
	```
	"""Multi target CLI"""

	import sys
	import json

	from rbkcli import RbkCli


	def rubrik_connect(args):
		"""Connect and run cmd to the instantiated rubrik connections."""

		# Convert args to a string separated by spaces
		str_args = ' '.join(args)

		# Declar var for all results.
		results = []

		# Declar and define auth for node 1.
		lab_auth_1 = {
			'server': '192.168.0.1',
			'username': 'admin', 
			'password': 'Password'
			}

		# Execute and save output to results.
		results.append(rbk_exec(lab_auth_1, str_args))

		# Declar and define auth for node 2.
		lab_auth_2 = {
			'server': '192.168.0.2',
			'username': 'admin', 
			'password': 'Password'
			}

		# Execute and save output to results.
		results.append(rbk_exec(lab_auth_2, str_args))

		# Declar and define auth for node 3.
		lab_auth_3 = {
			'server': '192.168.0.3',
			'username': 'admin', 
			'password': 'Password'
			}
			
		# Execute and save output to results.
		results.append(rbk_exec(lab_auth_3, str_args))

		return results

	def rbk_exec(auth, cmd):
		"""Instantiate connection and run command."""

		# Instantiate auth using authentication provided.
		node = RbkCli(auth=auth)

		# Execute command.
		output = node.execute(cmd)

		# Return command output in json.
		return json.loads(output)

	def main():
		"""Call rubrik connection and print the output."""
		
		# Treat args provided.
		args = sys.argv[1:]

		# Call instantiation and cmd execution.
		output = rubrik_connect(args)

		# Print output as json indented.
		print(json.dumps(output, indent=2))

	if __name__ == '__main__':
		main()
	```

2. Once the above script is saved as *multi_target.py*, it can be called in the following way:

	```
	$ multi_target.py node_management hostname
	[
	  "RVMHM184S001650",
	  "RVMHM184S001337",
	  "RVMHM184S001500"
	]
	```

### Explanation
Effectively we take the arguments passed to the script and pass it to all defined targets. When developing automation with **rbkcli** the main point you need to worry about is how to get the target information. 
You can create a dynamic script where the you provide the amount of targets you want to instantiate and their respective credentials, then run the commands based on that group.
Such automation can be very useful while configuring multiple clusters/edges at the same time, you can build up a configuration request for SLAs, for example, and send it to all targets.