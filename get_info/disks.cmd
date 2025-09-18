@echo off
setlocal enabledelayedexpansion

:: Storage Type
set "storage_type="
for /f "skip=3 tokens=* delims=" %%a in ('powershell -command "Get-PhysicalDisk | Sort-Object -Property DiskNumber | Select MediaType"') do (
    if not "%%a"=="" (
        set "storage_type=%%a"
        goto :gotDiskType
    )
)
:gotDiskType

echo !storage_type!
pause 
:: Initialize list variable
set "media_types="

:: Get disk info from PowerShell
for /f "skip=3 tokens=* delims=" %%a in ('powershell -NoProfile -Command "Get-PhysicalDisk | Sort-Object DiskNumber | Select MediaType, Size, SerialNumber"') do (
    rem Remove quotes from PowerShell output
    set "line=%%a"
    set "line=!line:\"=!"
    rem Append line to media_types with a line break
    if defined media_types (
        set "media_types=!media_types!|!line!"
    ) else (
        set "media_types=!line!"
    )
)

:: Display results
echo !storage_type!
echo Media Types:
echo !media_types!

echo.
echo done
pause
endlocal
