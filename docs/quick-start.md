# rbkcli

## Requirements

Before starting the installation make sure you match the following requirements
 - OS: 
	* Linux
	* Mac
	* Windows
 - Python:
	* python-3.5.6
	* python-3.6.9
	* python-3.7.3
 - pip (Python's package indexer)
 - setuptools (Python module that automates modules installation)
 
In order to install setuptools package you can run the following command:
 
```
$ pip install setuptools
```

For more information onhow to install Python for each platform please visit: [Python Software Foundation](https://www.python.org/)

## Installation

Option 1:
1. Install from source, using git command line:

```
$ git clone git@github.com:rubrikinc/rbkcli.git
$ cd rbkcli
$ python setup.py install
```

Option 2:
1. Install from Python Package Index, with pip:

```
$ pip install rbkcli
```

Post install:
1. Enable auto-complete (**only for bash environments**):
```
$ echo ' eval "$(register-python-argcomplete rbkcli)"' >> ~/.bashrc
$ . ~/.bashrc
```

## Configuring target

By default, the rbkcli will attempt to read the the Rubrik Cluster credentials from the following environment variables:

* `rubrik_cdm_node_ip`
* `rubrik_cdm_username`
* `rubrik_cdm_password`

You can also specify a token to be used in the authentication by exporting the following environment variable, but it is not required:
* `rubrik_cdm_token`

So for Linux/Mac systems the commands to be run would be:

```
$ export rubrik_cdm_node_ip=<IP>
$ export rubrik_cdm_username=<username>
$ export rubrik_cdm_password=<password>
$ export rubrik_cdm_token=<token>
```

For windows systems the commands to be run would be:

```
$ set rubrik_cdm_node_ip=<IP>
$ set rubrik_cdm_username=<username>
$ set rubrik_cdm_password=<password>
$ set rubrik_cdm_token=<token>
```

The token will take precedence over *username/password* authentication, once the token expires rbkcli will default back to username and password if provided.

## Example
Once the above environment variables are exported, rbkcli will dynamically create the command line based on the available APIs in that cluster.

```
$ rbkcli cluster me
EnvironmentHandler # No cached API found for this target, importing APIs...
{
  "acceptedEulaVersion": "0.0",
  "apiVersion": "1",
  "id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "latestEulaVersion": "1.1",
  "name": "MyCluster",
  "timezone": {
    "timezone": ""
  },
  "version": "4.2.2-1699"
}
```

At this point all rbkcli features should be available, including auto-complete.

## More information

For more information about rbkcli tool and its features go to:
* [About rbkcli](about.md)

For complete **rbkcli** usage and feature documentation go to:
* [Summary](SUMMARY.md)

