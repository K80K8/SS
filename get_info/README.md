This folder contains two batch files:

    get_info.cmd - to get data for computers to be donated
    get_info_listed.cmd - to get data for computers to be listed for sale

The batch files are run after a fresh windows install to collect information about computer specs, e.g. serial number, model, cpu type, etc.
They prompt user for some inputs, e.g. barcode number, windows version installed, etc.

There are two notebooks that explore processing the raw data and outputting into a desired format in a csv that can be directly imported into an Access database. The end-goal is to have a python script for data processing/cleansing.

Summary of process:
1) user installs windows from usb drive
2) user runs batch file (from usb drive) to collect data after fresh install
    - user chooses which batch file depending on whether computer listed or donated
3) data is ouput to server in text file
4) text file data is collated and processed using python script to generate csv
5) csv imported into Access