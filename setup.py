"""Setup module for rbkcli"""

import setuptools

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

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