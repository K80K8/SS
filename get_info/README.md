This folder contains a batch file called "get_info.cmd" to collect information about computers to be donated or listed for sale. The process is as follows:

1) user installs windows from usb drive
2) user runs batch file (from usb drive) to collect information after fresh install
3) user enters inputs:
   - whether computer is listed or added to system
   - barcode or listing number
   - corporate supplier (if applicable)
5) computer information is collected by script and ouput to server in text file
6) text file data is collated and processed using python script to generate csv
7) csv imported into Access database

There are 20 usb drives each which save the raw output from the get_info script to a server in a text file specific to the drive. For example, the drive labelled '1' will save into a file called 'info_vol1.txt', the drive labelled '2' will save to 'info_vol2.txt' and so on. This is to avoid collision of drives trying to read and write one file on the server at the same time.

Also within this folder is a powershell script called 'update_get_infos.ps1'. This updates the get_info code on 20 usb drives, should there be any edits to the original 'get_info.cmd' file. It copies the updated code over to the usb drive while maintaining the unique output filename for the usb drive.

The text files on the server can be downloaded then the python script called 'process_data.py' collates the data from the these files and outputs the correctly formatted data into 2 csv files: one for items to be listed for sale, and the other for items to be added to the system for donation. The filenames contain a datetime stamp to avoid overwriting a csv whenever a new batch of text files are processed. The csv files can be opened in excel as spreadsheets, and the format allows for importing the data into an Access database. 

There are also currently some Jupyter notebooks stored in the folder named 'experimental_code' that explore processing the raw data and outputting into a desired format in a csv that can be directly imported into an Access database. There is some sample data stored in the 'raw_data' folder for testing the script.

--------------------
SCRIPT NOT WORKING?
--------------------
If the python script is not working check you have the correct version of Python (3.8.10), and Python libraries installed:
   glob
   numpy
   pandas
   datetime