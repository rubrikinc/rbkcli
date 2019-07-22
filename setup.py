"""Setup module for rbkcli"""

import setuptools
import os
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError

LONG_DESCRIPTION = """
# rbkcli

This project provides a Command Line Interface (CLI) conversion of Rubrik APIs.
It can be used for both running commands or writing simplified scripts.

## Installation

Install from pip:

`pip install rbkcli`

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

## Documentation

Here are some resources to get you started! If you find any challenges from this project are not properly documented or are unclear, please raise an issueand let us know! This is a fun, safe environment - don't worry if you're a GitHub newbie! :heart:

* [Quick Start Guide](https://github.com/rubrikinc/rbkcli/blob/master/docs/quick-start.md)
* [Documentation Summary](https://github.com/rubrikinc/rbkcli/blob/master/docs/SUMMARY.md)
* [Rubrik API Documentation](https://github.com/rubrikinc/api-documentation)

## How You Can Help

We glady welcome contributions from the community. From updating the documentation to adding more functions for Python, all ideas are welcome. Thank you in advance for all of your issues, pull requests, and comments! :star:

* [Contributing Guide](https://github.com/rubrikinc/rbkcli/blob/master/CONTRIBUTING.md)
* [Code of Conduct](https://github.com/rubrikinc/rbkcli/blob/master/CODE_OF_CONDUCT.md)

## License

* [MIT License](https://github.com/rubrikinc/rbkcli/blob/master/LICENSE)

## About Rubrik Build

We encourage all contributors to become members. We aim to grow an active, healthy community of contributors, reviewers, and code owners. Learn more in our [Welcome to the Rubrik Build Community](https://github.com/rubrikinc/welcome-to-rubrik-build) page.

We'd  love to hear from you! Email us: build@rubrik.com


"""


def create_structure():
    """For scripts and cmdlets provided with package."""
    dir_structure = ['~/rbkcli',
                     '~/rbkcli/conf',
                     '~/rbkcli/conf/cmdlets',
                     '~/rbkcli/scripts']

    for file in dir_structure:
        try:
            file = os.path.expanduser(file)
            if not os.path.isdir(file):
                os.mkdir(file)
            if 'cmdlets' in file:
                copy_tree('cmdlets/', file)
            if 'scripts' in file:
                copy_tree('scripts/', file)

        except PermissionError as error:
            pass
        except FileNotFoundError as error:
            pass
        except DistutilsFileError as error:
            pass


setuptools.setup(
    name='rbkcli',
    version='1.0.0',
    author='Bruno Manesco',
    author_email='bruno.manesco@rubrik.com',
    description='A python package that creates a CLI conversion from Rubrik APIs',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/rubrikinc/rbkcli',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'Paramiko',
        'argcomplete',
        'PyYAML',
        'urllib3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points="""
      [console_scripts]
      rbkcli = rbkcli.interface.rbk_cli:main
      """,
)

create_structure()
