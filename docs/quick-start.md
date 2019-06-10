# rbkcli

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

Once the above environment variables are exported, rbkcli will dynamically create the command line based on the available APIs in that cluster.

```
$ rbkcli cluster me
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

## More information

For more information about rbkcli tool and its features go to:
* [About rbkcli](about.md)

