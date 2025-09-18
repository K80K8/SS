This folder contains a batch file called "get_info.cmd" to collect information about computers to be donated or listed for sale. The process is as follows:

1) user installs windows from usb drive
2) user runs batch file (from usb drive) to collect information after fresh install
3) user enters inputs:
   - whether computer is listed or added to system
   - barcode or listing number
   - corporate supplier (if applicable)
5) computer information is collected by script and ouput to server in text file
6) text file data is collated and processed using python script to generate csv
7) csv imported into Access

There are also currently some notebooks that explore processing the raw data and outputting into a desired format in a csv that can be directly imported into an Access database. The end-goal is to have a python script for data processing/cleansing.
