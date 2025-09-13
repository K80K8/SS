@echo off
setlocal enabledelayedexpansion

@REM net use Z: "\\IPaddress\folder" /user:username password

@REM set "outfile=\\IPaddress\folder\filename.txt"

set "outfile=test.txt"

rem === Check if file exists; if not, add headers ===
if not exist "%outfile%" (
    echo Number,Model,CPU,CPUCores,RAMAmount,RAMType,StorageAmount,StorageType,Windows,WindowsActivated> "%outfile%"
)

rem === Prompt for Number ===
set /p "number=Please enter the number of this device: "
set /p "windows=Please enter Windows Type Version: "

:Ask
set /P win_activated="Has Windows been activated? (Y/N): "
if /I "%win_activated%"=="y" goto entered
if /I "%win_activated%"=="n" goto entered
echo Invalid input. Please enter Y or N.
goto Ask
:entered

rem === Get Model ===
set "model="
for /f "skip=1 tokens=* delims=" %%a in ('wmic computersystem get model') do (
    if not "%%a"=="" (
        set "model=%%a"
        goto :gotModel
    )
)
:gotModel

rem === Get CPU Name ===
set "cpu="
for /f "skip=1 tokens=* delims=" %%a in ('wmic cpu get name') do (
    if not "%%a"=="" (
        set "cpu=%%a"
        goto :gotCPU
    )
)
:gotCPU

rem === Get CPU Cores ===
set "cores="
for /f "skip=1 tokens=* delims=" %%a in ('wmic cpu get NumberOfCores') do (
    if not "%%a"=="" (
        set "cores=%%a"
        goto :gotCores
    )
)
:gotCores

rem === Get RAM Amount in Bytes ===
set "ram_amt="
for /f "skip=1 tokens=* delims=" %%a in ('wmic ComputerSystem get TotalPhysicalMemory') do (
    if not "%%a"=="" (
        set "ram_amt=%%a"
        goto :gotRam
    )
)
:gotRam

rem === Get RAM Type Code ===
set "ram_type="
for /f "skip=1 tokens=* delims=" %%a in ('wmic memoryChip get SMBIOSMemoryType') do (
    if not "%%a"=="" (
        set "ram_type=%%a"
        goto :gotRamType
    )
)
:gotRamType

rem === Get Storage Disk Drive Size in Bytes ===
set "storage_amt="
for /f "skip=1 tokens=* delims=" %%a in ('wmic diskdrive get size') do (
    if not "%%a"=="" (
        set "storage_amt=%%a"
        goto :gotDiskSize
    )
)
:gotDiskSize

rem === Get Storage Disk Drive Type ===
set "storage_type="
@REM for /f "skip=1 tokens=* delims=" %%a in ('wmic diskdrive get MediaType') do (
for /f "skip=3 tokens=* delims=" %%a in ('powershell -command "Get-PhysicalDisk | Select MediaType"') do (
    if not "%%a"=="" (
        set "storage_type=%%a"
        goto :gotDiskType
    )
)
:gotDiskType

rem === Trim spaces ===
for /f "tokens=* delims= " %%A in ("!model!") do set "model=%%A"
for /f "tokens=* delims= " %%A in ("!cpu!") do set "cpu=%%A"
for /f "tokens=* delims= " %%A in ("!cores!") do set "cores=%%A"
for /f "tokens=* delims= " %%A in ("!ram_amt!") do set "ram_amt=%%A"
for /f "tokens=* delims= " %%A in ("!ram_type!") do set "ram_type=%%A"
for /f "tokens=* delims= " %%A in ("!storage_amt!") do set "storage_amt=%%A"
for /f "tokens=* delims= " %%A in ("!storage_type!") do set "storage_type=%%A"

rem === Append CSV line ===
echo !number!,!model!,!cpu!,!cores!,!ram_amt!,!ram_type!,!storage_amt!,!storage_type!,!windows!,!win_activated!>> "%outfile%"

endlocal