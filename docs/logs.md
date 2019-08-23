# Logs

## Location
The default logging level for rbkcli is debug. As mentioned in the [Folder Structure](folder_structure.md) section, the log file is auto generated at ```-/home/<user>/rbkcli/logs/rbkcli.log```.

## Rotation
The log file will auto rotate when it reaches the size of 2 MB, the maximum allowed amount of files is the “current” logging file plus 5 rotated files. Therefore the log folder should not take more than 12MB when full.

## Available information
The log file stores information related to the rbkcli run time such as: target IP, Rubrik cluster ID, the provided arguments from the CLI, what user profile was used to load the commands available and what API is being executed. Besides the mentioned actions, it also logs validation for any information that needs to be loaded.
