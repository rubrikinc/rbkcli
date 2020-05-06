# INSTALLATION

0. Make sure you meet the requirements OS, Python, pip:
	```
	$ python -V
	$ 
	$ python3 -V
	$ pip3 list
	$ pip3 list | grep "setup"
	```

1. Install git and python-argcomplete on your Linux box:
	```
	$ sudo apt install git
	$ sudo apt install python-argcomplete
	```

2. Download rbkcli and rename the downloaded folder to avoid future conflict:
	```
	$ git clone https://github.com/rubrikinc/rbkcli.git
	$ mv rbkcli/ rbkcli-pkg
	```

3. Install rbkcli:
	```
	$ cd rbkcli-pkg/
	$ python3 -m pip install .
	```
	
	If the above command could not install the package successfully proceed running the following.
	```
	$ sudo python3 setup.py install
	```

4. Configure rbkcli auto-complete:
	```
	$ echo ' eval "$(register-python-argcomplete rbkcli)"' >> ~/.bashrc
	$ . ~/.bashrc
	```

5. Configure rbkcli session:
- Run the commands:
	```
	export rubrik_cdm_node_ip="192.168.1.220"
	export rubrik_cdm_username="admin"
	export rubrik_cdm_password="Rubrik123!!"
	```
- Or less secure, add it to .bashrc file:
	```
	vi ~/.bashrc
	```
- Add the following by the end of the file:
	```
	# rbkcli env
	eval "$(register-python-argcomplete rbkcli)"
	export rubrik_cdm_node_ip="192.168.1.220"
	export rubrik_cdm_username="admin"
	export rubrik_cdm_password="Rubrik123!!"
	```
- Reload .bashrc file:
	```
	. ~/.bashrc
	```

6. Test connection:
	```
	$ rbkcli cluster me
	EnvironmentHandler # No cached API found for this target, importing APIs...
	Could not import Google libraries.  /home/rksupport/rbkcli/scripts/default/gmailer.py
	Please access: https://developers.google.com/gmail/api/quickstart/python
	{
	  "id": "616fdf1b-68ea-4ec0-84a1-8bea2b9c51fb",
	  "version": "5.1.1-8049",
	  "apiVersion": "1",
	  "name": "rubrik-hq",
	  "timezone": {
		"timezone": ""
	  },
	  "acceptedEulaVersion": "1.1",
	  "latestEulaVersion": "1.1"
	}
	```
