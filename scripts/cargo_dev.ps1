param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CargoArgs = @("check", "-q")
)

$ErrorActionPreference = "Stop"

$vsDevCandidates = @(
    "C:\Program Files\Microsoft Visual Studio\18\Enterprise\Common7\Tools\VsDevCmd.bat",
    "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat",
    "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\Tools\VsDevCmd.bat",
    "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat",
    "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
)

$vsDevCmd = $vsDevCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $vsDevCmd) {
    throw "VsDevCmd.bat nuk u gjet. Instalo Visual Studio C++ Build Tools (Desktop development with C++)."
}

$argsEscaped = ($CargoArgs | ForEach-Object {
        '"' + ($_ -replace '"', '\"') + '"'
    }) -join ' '

$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$cmd = 'call "{0}" -arch=x64 -host_arch=x64 ^&^& cd /d "{1}" ^&^& cargo {2}' -f $vsDevCmd, $workspace, $argsEscaped

cmd.exe /d /s /c $cmd
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}