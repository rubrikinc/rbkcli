# rbkcli

This project provides a Command Line Interface (CLI) conversion of Rubrik APIs.
It can be used for both running commands or writing simplified scripts.

## Installation

Install from PyPI:

```
$ pip install rbkcli
$ echo 'eval "$(register-python-argcomplete rbkcli)"' >> ~/.bashrc
```

## Example

By default, the rbkcli will attempt to read the the Rubrik Cluster credentials from the following environment variables:
* `rubrik_cdm_node_ip`
* `rubrik_cdm_username`
* `rubrik_cdm_password`
So the commands to be run would be:

```
$ export rubrik_cdm_node_ip=<IP>
$ export rubrik_cdm_username=<username>
$ export rubrik_cdm_password=<password>
```

Once the above environment variables are exported with the authentication data, *rbkcli* will dynamically create the command line based on the available APIs in that cluster.

`$ rbkcli cluster me`

![rbkcli cluster me output](https://user-images.githubusercontent.com/8610203/61711662-2f8c7580-ad1a-11e9-9ab2-6bcae2bb1f33.png)

## Documentation
* [Quick Start Guide](https://github.com/rubrikinc/rbkcli/blob/master/docs/quick-start.md)
* [rbkcli Documentation](https://rubrik.gitbook.io/rbkcli/)
* [Rubrik API Documentation](https://github.com/rubrikinc/api-documentation)