[xml]$b = Get-Content "C:/Users/User/battery-report.xml"

$b.BatteryReport.Batteries.Battery | ForEach-Object {
    [PSCustomObject]@{
        DesignCapacity     = $_.DesignCapacity
        FullChargeCapacity = $_.FullChargeCapacity
        CycleCount         = $_.CycleCount
        Health             = ("{0:N2}%%" -f (($_.FullChargeCapacity -as [double]) / ($_.DesignCapacity -as [double]) * 100))
    }
}