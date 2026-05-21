#!/usr/bin/env pwsh

param(
    [Parameter(Position = 0)]
    [string]$Target = 'help',

    [Parameter(Position = 1)]
    [string]$ComposeFile = 'docker-compose.yml'
)

$ScriptPath = Join-Path $PSScriptRoot 'scripts/kloud-make.ps1'
& $ScriptPath $Target $ComposeFile
