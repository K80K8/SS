The report generator reads in data from Blancco data erasure reports in xml format and collates relevant information into an excel spreadsheet.

Click on bat file to run code. Choose folder containing Blancco reports, and then choose output folder for spreadsheet.

If code is not running try the following:

1) Open Powershell as Administrator, then run this command:
        
        Install-Module -Name ImportExcel -Scope CurrentUser

2) To allow local scripts and signed remote scripts to run in Powershell, run these commands (in Powershell):

        Get-ExecutionPolicy
        Set-ExecutionPolicy RemoteSigned