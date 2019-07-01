# rbkcli

## Requirements

Before starting the installation make sure ou match the following requirements
 - OS: Linux/Mac
 - Python3.5+
 - pip3 (Python's package indexer)
 - setuptools (Python module that automates moddules instalation)
 
 In order to install the requirements you can run the following commands:
 
 ```
 $ sudo apt install python3
 $ sudo apt install python3-pip
 $ pip3 install setuptools
 ```

## Installation

Install from source and enable autocomplete:

```
$ git clone git@github.com:rubrikinc/rbkcli.git
$ cd rbkcli
$ python setup.py install
$ echo ' eval "$(register-python-argcomplete rbkcli)"' >> ~/.bashrc
```

## Example

By default, the rbkcli will attempt to read the the Rubrik Cluster credentials from the following environment variables:

* `rubrik_cdm_node_ip`
* `rubrik_cdm_username`
* `rubrik_cdm_password`

You can also specify a token to be used in the authentication by exporting the following evironment variable:
* `rubrik_cdm_token`

So the commands to be run would be:

```
$ export rubrik_cdm_node_ip=<IP>
$ export rubrik_cdm_username=<username>
$ export rubrik_cdm_password=<password>
$ export rubrik_cdm_token=<token>
```

The token will take precedence over *username/password* authentication, once the token expires rbkcli will default back to username and password if provided.
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

At this point all rbkcli features should be available, including autocomplete.

## More information

For more information about rbkcli tool and its features go to:
* [About rbkcli](about.md)

For complete **rbkcli** usage and feature documentation go to:
* [Summary](SUMMARY.md)
