# rbkcli Portable

## What is it?
It is an executable file (.pex), which you can run in your environment without having to install any other python module.
The **.pex** file is created with a minimum environment, containing all necessary packages to run sealed.

## Packages
Following are the packages present in rbkcli.pex file:
 - argcomplete 1.10.0ributions :: Packaging pycparser
 - bcrypt 3.1.6
 - chardet 3.0.4
 - idna 2.8
 - cffi 1.12.3
 - certifi 2019.3.9
 - cryptography 2.7
 - pycparser 2.19
 - PyYAML 5.1.1
 - asn1crypto 0.24.0
 - PyNaCl 1.3.0
 - urllib3 1.25.3
 - requests 2.22.0
 - six 1.12.0
 - paramiko 2.5.0
 - rbkcli 1.0.0

## Implications
The result of running the .pex file will be exactly the same as running the installed module, but there are features that won't be available in the portable version:
 - auto-completion: Auto-completion is a result of the interaction between argcomplete and Linux bash environment and setuptools creating a entry point for rbkcli. Once the setup file is not executed and most environments don't have argcomplete installed, auto-completion is not available.
 - rbkcli SDK: Once the rbkcli module will not be installed, users won't be able to create customized scripts that are independent from the rbkcli.pex file (call RbkCli). The custom scripts added as part of rbkcli will still be ran normally (class RbkCliBlackOps).

## Versions
The .pex can contain all packages that are required for rbkcli to run, currently with the above set of packages, **rbkcli** has released a beta executable.
 - [rbkcli-1.0.0b0.pex](https://github.com/rubrikinc/rbkcli/releases/tag/v1.0.0-beta.0%2Bportable): Can be used in any Linux box, with the interpreter in the following versions:
    * Python3.5
    * Python3.6
    * Python3.7
