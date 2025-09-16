@echo off
setlocal enabledelayedexpansion
@REM net use Z: "\\192.168.1.32\Data Entry" /user:DataEntry password

@REM set "outfile=\\192.168.1.32\Data Entry\test.txt"

set "outfile=test.txt"

rem === Check if file exists. If not, add headers ===
if not exist "%outfile%" (
    echo Barcode,Manufacturer,Model,SerialNumber,CPU,Corporate Supplier> "%outfile%"
)

rem === Prompt for barcode ===
set /p "barcode=Please scan or enter the barcode: "
set /p "corp=Please enter the corporate supplier: "

rem === Get Manufacturer ===
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

rem === Get Model ===
set "model="
for /f "skip=1 delims=" %%a in ('wmic computersystem get model') do (
    set "line=%%a"
    if defined line (
        for /f "tokens=* delims=" %%b in ("!line!") do (
            set "model=%%b"
            goto :next2
        )
    )
)
:next2

rem === Get Serial Number ===
set "serial="
for /f "skip=1 delims=" %%a in ('wmic bios get serialnumber') do (
    set "line=%%a"
    if defined line (
        for /f "tokens=* delims=" %%b in ("!line!") do (
            set "serial=%%b"
            goto :next3
        )
    )
)
:next3

rem === Get CPU Name ===
set "cpu="
for /f "skip=1 delims=" %%a in ('wmic cpu get name') do (
    set "line=%%a"
    if defined line (
        for /f "tokens=* delims=" %%b in ("!line!") do (
            set "cpu=%%b"
            goto :output
        )
    )
)

:output
rem === Append CSV line ===
echo !barcode!,!manufacturer!,!model!,!serial!,!cpu!,!corp!>> "%outfile%"