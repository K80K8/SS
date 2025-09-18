@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: Output file (defaulting to local, can be set to network path if needed)
:: ============================================================================
:: net use Z: "\\192.168.1.32\Data Entry" /user:DataEntry password
:: set "outfile=\\192.168.1.32\Data Entry\info_vol0.txt"
set "outfile=info_vol0.txt"

:: ============================================================================
:: Create file with headers if it does not exist
:: ============================================================================
if not exist "%outfile%" (
    echo ForSystem,Barcode,Manufacturer,Model,SerialNumber,CPU,CPUCores,RAMAmount,RAMType,StorageAmount,StorageType,CorporateSupplier,Windows,WindowsActivated> "%outfile%"
)

:: ============================================================================
:: Ask user for mode: Add to System (1) or Prepare for Sale (0)
:: ============================================================================
:ask
echo.
echo Enter 1 for Adding Laptop to the System
echo Enter 0 for Preparation for Sale
set /p "choice=Your choice: "

if "%choice%"=="1" (
    echo You entered 1.
    goto :gotChoice
) else if "%choice%"=="0" (
    echo You entered 0.
    goto :gotChoice
) else (
    echo Invalid input. Please enter 1 or 0.
    goto :ask
)

:gotChoice

:: ============================================================================
:: Get listing number or barcode, and optionally supplier
:: ============================================================================
if "%choice%"=="1" (
    :getNumber
    set /p "number=Please scan or enter the Barcode of this device: "
    if not defined number (
        echo You must enter a Barcode.
        goto :getNumber
    ) 
    set /p "corp=Please enter the corporate supplier if applicable: "
    goto gotCode
) else (
    :getListing
    set /p "number=Please enter the Listing Number of this device: "
    if not defined number (
        echo You must enter a Listing Number.
        goto :getListing
    )
    set "corp="
    goto gotCode
)
:gotCode

:: ============================================================================
:: Collect system information
:: ============================================================================

:: Manufacturer
set "manufacturer="
for /f "skip=1 delims=" %%a in ('wmic computersystem get manufacturer') do (
    set "line=%%a"
    if defined line (
        for /f "tokens=* delims=" %%b in ("!line!") do (
            set "manufacturer=%%b"
            goto :gotManufacturer
        )
    )
)
:gotManufacturer

:: Serial Number
set "serial="
for /f "skip=1 delims=" %%a in ('wmic bios get serialnumber') do (
    set "line=%%a"
    if defined line (
        for /f "tokens=* delims=" %%b in ("!line!") do (
            set "serial=%%b"
            goto :gotSerial
        )
    )
)
:gotSerial

:: Windows Version
set "windows="
for /f "skip=1 tokens=* delims=" %%a in ('wmic os get caption') do (
    if not "%%a"=="" (
        rem Trim leading/trailing whitespace
        for /f "tokens=* delims= " %%b in ("%%a") do set "windows=%%b"
        goto :gotWindows
    )
)
:gotWindows

:: Windows Activation Status
set "win_activated="
for /f "skip=1 tokens=* delims=" %%a in ('cscript //nologo "%systemroot%\system32\slmgr.vbs" /xpr') do (
    if not "%%a"=="" (
        rem Remove leading spaces/tabs
        for /f "tokens=* delims= " %%b in ("%%a") do set "win_activated=%%b"
        goto :gotActivated
    )
)
:gotActivated

:: Model
set "model="
for /f "skip=1 tokens=* delims=" %%a in ('wmic computersystem get model') do (
    if not "%%a"=="" (
        set "model=%%a"
        goto :gotModel
    )
)
:gotModel

:: CPU Name
set "cpu="
for /f "skip=1 tokens=* delims=" %%a in ('wmic cpu get name') do (
    if not "%%a"=="" (
        set "cpu=%%a"
        goto :gotCPU
    )
)
:gotCPU

:: CPU Cores
set "cores="
for /f "skip=1 tokens=* delims=" %%a in ('wmic cpu get NumberOfCores') do (
    if not "%%a"=="" (
        set "cores=%%a"
        goto :gotCores
    )
)
:gotCores

:: RAM Amount
set "ram_amt="
for /f "skip=1 tokens=* delims=" %%a in ('wmic ComputerSystem get TotalPhysicalMemory') do (
    if not "%%a"=="" (
        set "ram_amt=%%a"
        goto :gotRam
    )
)
:gotRam

:: RAM Type
set "ram_type="
for /f "skip=1 tokens=* delims=" %%a in ('wmic memoryChip get SMBIOSMemoryType') do (
    if not "%%a"=="" (
        set "ram_type=%%a"
        goto :gotRamType
    )
)
:gotRamType

:: Storage Size
set "storage_amt="
for /f "skip=1 tokens=* delims=" %%a in ('wmic diskdrive get size') do (
    if not "%%a"=="" (
        set "storage_amt=%%a"
        goto :gotDiskSize
    )
)
:gotDiskSize

:: Storage Type
set "storage_type="
for /f "skip=3 tokens=* delims=" %%a in ('powershell -command "Get-PhysicalDisk | Sort-Object -Property DiskNumber | Select MediaType"') do (
    if not "%%a"=="" (
        set "storage_type=%%a"
        goto :gotDiskType
    )
)
:gotDiskType

:: ============================================================================
:: Trim spaces from values
:: ============================================================================
for /f "tokens=* delims= " %%A in ("!model!")        do set "model=%%A"
for /f "tokens=* delims= " %%A in ("!cpu!")          do set "cpu=%%A"
for /f "tokens=* delims= " %%A in ("!cores!")        do set "cores=%%A"
for /f "tokens=* delims= " %%A in ("!ram_amt!")      do set "ram_amt=%%A"
for /f "tokens=* delims= " %%A in ("!ram_type!")     do set "ram_type=%%A"
for /f "tokens=* delims= " %%A in ("!storage_amt!")  do set "storage_amt=%%A"
for /f "tokens=* delims= " %%A in ("!storage_type!") do set "storage_type=%%A"

:: ============================================================================
:: Append results to CSV
:: ============================================================================
echo !choice!,!number!,!manufacturer!,!model!,!serial!,!cpu!,!cores!,!ram_amt!,!ram_type!,!storage_amt!,!storage_type!,!corp!,!windows!,!win_activated!>> "%outfile%"

echo done
pause
endlocal
