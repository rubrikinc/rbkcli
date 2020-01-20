"""Setup module for rbkcli"""

import setuptools
import os
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError

with open('docs/README-PIP.md', 'r') as fh:
    long_description = fh.read()


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
    version='1.0.0-beta.3',
    author='Bruno Manesco',
    author_email='bruno.manesco@rubrik.com',
    description='A python package that creates a CLI conversion from Rubrik APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rubrikinc/rbkcli',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'Paramiko',
        'argcomplete',
        'PyYAML',
        'urllib3',
        'jinja2',
        'python-dateutil'
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
