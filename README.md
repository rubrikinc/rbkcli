# rbkcli

This project provides a Command Line Interface (CLI) convertion of Rubrik APIs.
It can be used for both running commands or writing simplified scripts.

## :hammer: Installation

Install from source and enable autocomplete:

'''
$ git clone https://github.com/rubrikinc/rbkcli.git
$ cd rbkcli
$ python setup.py install
$ echo 'eval "$(_RBKCLI_COMPLETE=source rbkcli)"' >> ~/.bashrc
'''

## :mag: Example

By default, the rbkcli will attempt to read the the Rubrik Cluster credentials from the following environment variables:

* `<rubrik_cdm_node_ip>`
* `<rubrik_cdm_username>`
* `<rubrik_cdm_password>`

Once the above environment variables are exported, rbkcli will dynamically create the command line based on the available APIs in that cluster.

'''
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
'''

## :blue_book: Documentation

Here are some resources to get you started! If you find any challenges from this project are not properly documented or are unclear, please raise an issueand let us know! This is a fun, safe environment - don't worry if you're a GitHub newbie! :heart:

* Quick Start Guide
* [Rubrik API Documentation](https://github.com/rubrikinc/api-documentation)

## :muscle: How You Can Help

We glady welcome contributions from the community. From updating the documentation to adding more functions for Python, all ideas are welcome. Thank you in advance for all of your issues, pull requests, and comments! :star:

* [Contributing Guide](CONTRIBUTING.md)
* [Code of Conduct](CODE_OF_CONDUCT.md)

## :pushpin: License

* [MIT License](LICENSE)

## :point_right: About Rubrik Build

We encourage all contributors to become members. We aim to grow an active, healthy community of contributors, reviewers, and code owners. Learn more in our [Welcome to the Rubrik Build Community](https://github.com/rubrikinc/welcome-to-rubrik-build) page.

We'd  love to hear from you! Email us: build@rubrik.com :love_letter:
