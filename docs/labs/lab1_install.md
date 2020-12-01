
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
	
	If the above command could not install the package successfully, or if the `rbkcli` alias is not added to the shell, proceed running the following.
	```
	$ sudo python3 setup.py install
	```

4. Configure rbkcli auto-complete:
    - This step will change the `~/.bashrc` file, before making any changes let's create a backup copy of the file and move forward.
        ```
        $ cp ~/.bashrc ~/bashrc-OLD
        ```
    - Now add the line to the file:
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
    - Be aware that most shell environments have special characters interpretation, for example the `!` (exclamation mark) in bash. Therefore when passing a password through a shell command, you might need to escape that character, using a `\` (backslash) as following:
        ```
        $ export rubrik_cdm_password="Rubrik123\!\!"
        ```
    - Or less secure, add it to .bashrc file (if you did not create a backup copy of the `~/.bashrc` file on step 4, now is a good time):
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
    - You dont need to add `register-python-argcomplete` if you ran step 4 successfully, just re-arrange the file so its all organized  . 
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


<-- Back to [Useful learning workflows](labs.md)
