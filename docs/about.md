# About rbkcli
This project provides a Command Line Interface (CLI) conversion of Rubrik APIs. It can be used for both running commands or writing simplified scripts.

## Definition

The CLI part of rbkcli is dynamically generated, based on the API documentation of the provided target (rubrik_cdm_node_ip), because of that the available commands will vary according to the target provided.
rbkcli works as API proxy, where it converts the commands entered into RESTful APIs to Rubrik cluster. It also provides easy ways to find the API you want to use and its documentation.
The importing of APIs for each target only happens once, that is when the first command is run. After that we keep a local map to the environment cached, so in the case of using a different node from the same cluster as a target, the cached map provides resolution and rbkcli does not need to import the APIs again.
All available commands and parameters are "autocompletable" and the module has a configuration file (~/rbkcli/conf/rbkcli.conf) that allows a minimum degree of customization.

## Features
Current set of features are:
 - Low maintenance, changes according to target.
 - Auto-complete enable for all added operations.
 - Logging. By default there is debug level logging at "~/rbkcli/logs/rbkcli.log", the logs auto-rotate and only keep a maximum of 5 files of 2 megabytes each.
 - Output customization for JSON outputs, select the fields you like and convert output to table format.
 - API loops, loop the result of a API to another API, facilitating gathering more details.
 - Add cmdlets alias, each user can create their own command alias for commands more frequently ran.
 - User generated scripts to be automatically added as an available command ("autocompletable"), to facilitate customization and daily tasks.

## Planned Features
rbkcli is a public Rubrik Build project where anyone can contribute:
 - Create target groups, where one command is ran to all targets sequentially.
 - Add secure wallet to allow switching targets on the fly.

## Knowledge requirements:
In order to use rbkcli in its full potential, there are a couple of knowledge areas that are required:
- **Linux:** The initial setup requires some Linux knowledge, for day-to-day usage of the tool Linux knowledge is not essential.
- **RESTful APIs:** The user should have basic knowledge of APIs and its methods, once the tool is based on RESTful API documentation.
- **json:** Be familiarized with this particular notation, it can hold complex data and with the right language it allows a great deal of manipulation. This is the default output for all commands in rbkcli and its customization are based on the same principles. In order to get only the desired data and printed in a manner that matches expectation json knowledge is essential.
- **Python:** One of the rbkcli features is to convert custom scripts into callable, auto-completable commands. In order to make best use of this feature, users need to know how to code in Python.
- **Rubrik:** To be able to get the data needed the user needs to understand how Rubrik objects are organized and how they relate to each other.

## Documentation
The following page contains all the links to all documentation available on GitHub.
* [Summary](SUMMARY.md)
 
## Feedback
We are craving for feedback, so send them all!
