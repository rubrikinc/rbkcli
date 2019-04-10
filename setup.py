import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rbkcli",
    version="1.0.0",
    author="Bruno Manesco",
    author_email="bruno.manesco@rubrik.com",
    description="CLI conversion from Rubrik APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rubrikinc/rbkcli",
    packages=setuptools.find_packages(),
    install_requires=[
        'Click',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points="""
      [console_scripts]
      rbkcli = rbkcli.rbk_cli:main
      """,
)
