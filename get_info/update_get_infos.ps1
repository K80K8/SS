# MakeInfoCopies.ps1

$template = 'get_info.cmd'
$base     = 'Get_Infos'                # parent folder containing INFO 1..INFO 20

1..20 | ForEach-Object {
    $i = $_
    $folder = Join-Path $base ("INFO {0}" -f $i)
    New-Item -Path $folder -ItemType Directory -Force | Out-Null

    # Read the template and replace only the outfile line, leave everything else untouched
    Get-Content -LiteralPath $template | ForEach-Object {
        if ($_ -match '^\s*set\s+"outfile=') {
            # produce: set "outfile=info_volN.txt"
            "set `"outfile=info_vol{0}.txt`"" -f $i
        } else {
            $_
        }
    } | Set-Content -LiteralPath (Join-Path $folder 'get_info.cmd')
}

Write-Host "Done - created 20 copies in $base\INFO 1..INFO 20"
