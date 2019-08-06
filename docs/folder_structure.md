# Folder Structure

Once **rbkcli** is installed or (in the portable case) ran, it will create a set of folders and files in the user's home directory (~/rbkcli).
1. Following is an example of the folder structure:
	```
	$ tree ~/rbkcli
	/home/bmanesco/rbkcli
	├── conf
	│   ├── cmdlets
	│   │   └── rbkcli-cmdlets.json
	│   ├── rbkcli.conf
	│   └── target_resolution.json
	├── logs
	│   └── rbkcli.log
	├── scripts
	│   └── default
	│       ├── jsonfy_csv.py
	│       ├── jsonfy_report_table.py
	│       ├── log_api_metrics.py
	│       ├── log_bundle.py
	│       └── vmware_vm_protect_vms.py
	└── targets
		└── a8cd537d-e274-46d8-871e-f80ac47c264c
			└── me.json
	7 directories, 10 files
	```
	The folders structure will vary according to the, cmdlets profile you have or custom scripts that have already been added, but the default structure should be very similar to this one.
	
## Breakdown

1. conf/
	The *conf* folder contains 1 directory and 2 files.
    * The *cmdlets* folder, contains the cmdlets profiles created by the users. Each profile corresponds to a json file. 
        - When installed **rbkcli** comes with rbkcli-cmdlets.json profile.
    * The *rbkcli.conf* file is the configuration file where users can change settings and API profiles.
    	- For more information on configuration changes, visit: [Configuration File](configuration_file.md)
	* The *target_resolution.json* file, is **rbkcli's** map to optimize caching for each target. Once rbkcli is used against a target, one of the files created/updated is *target_resolution.json* file. 
		- rbkcli uses this file to decide whether or not if there is already a copy of the API documentation cached in the local system.
		- For tweaking options please visit: [Use rbkcli with a proxy/VPN](KB0017.md)

2. logs/
	The *logs* folder contains auto-generated log files, this folder can have 1 current log plus 5 rolled logs, the maximum size of the each file is 2Mb.
	- For more information on logs available, visit logs documentation at: [Logs](logs.md)

3. scripts/
	The *scripts* folder contains 1 directory, but can me modified at will by any user.
	* The *default* folder contains the scripts release with **rbkcli** public version, the **rbkcli** library that differentiates from simple API calls.

4. targets/
	The *targets* folder will contain a directory per unique cluster which **rbkcli** has connected to. This is the folder that holds the cached data of each target.
	* The *<cluster_uuid>* folder contains 1 file called me.json, which is essentially the cached information of the whole API documentation.