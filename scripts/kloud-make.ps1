#!/usr/bin/env pwsh

param(
    [Parameter(Position = 0)]
    [ValidateSet('help','up','down','stop','start','restart','build','rebuild','pull','ps','logs','life','cdm','end2end','doctor','airflow','init-db','seed-neo','fabric-up','fabric-down')]
    [string]$Target = 'help',

    [Parameter(Position = 1)]
    [string]$ComposeFile = 'docker-compose.yml'
)

$ErrorActionPreference = 'Stop'

function Invoke-Compose {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    & docker compose -f $ComposeFile @Args
}

function Show-Help {
    Write-Host 'Kloud PowerShell Make Targets'
    Write-Host '  ./make.ps1 up          - Start stack in detached mode'
    Write-Host '  ./make.ps1 down        - Stop and remove stack'
    Write-Host '  ./make.ps1 stop        - Stop stack without removing'
    Write-Host '  ./make.ps1 start       - Start existing containers'
    Write-Host '  ./make.ps1 restart     - Restart stack'
    Write-Host '  ./make.ps1 build       - Build images'
    Write-Host '  ./make.ps1 rebuild     - Rebuild images without cache'
    Write-Host '  ./make.ps1 pull        - Pull latest images'
    Write-Host '  ./make.ps1 ps          - Show container status'
    Write-Host '  ./make.ps1 logs        - Follow compose logs'
    Write-Host '  ./make.ps1 life        - Quick health/status checks'
    Write-Host '  ./make.ps1 cdm         - Clean deploy mode (end-to-end)'
    Write-Host '  ./make.ps1 end2end     - Alias for cdm'
    Write-Host '  ./make.ps1 doctor      - Environment diagnostics'
    Write-Host '  ./make.ps1 airflow     - List airflow DAGs'
    Write-Host '  ./make.ps1 init-db     - Initialize postgres extensions'
    Write-Host '  ./make.ps1 seed-neo    - Seed Neo4j ontology'
    Write-Host '  ./make.ps1 fabric-up   - Start clx fabric compose'
    Write-Host '  ./make.ps1 fabric-down - Stop clx fabric compose'
    Write-Host ''
    Write-Host "Compose file in use: $ComposeFile"
}

function Invoke-Life {
    Invoke-Compose -Args @('ps')

    Write-Host '[life] checking core health endpoints...'
    try {
        $null = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5
        Write-Host '[life] ok: http://localhost:8000/health'
    }
    catch {
        Write-Host '[life] warn: http://localhost:8000/health not ready'
    }

    try {
        $null = Invoke-WebRequest -Uri 'http://localhost:8000/status' -UseBasicParsing -TimeoutSec 5
        Write-Host '[life] ok: http://localhost:8000/status'
    }
    catch {
        Write-Host '[life] warn: http://localhost:8000/status not ready'
    }
}

function Invoke-Cdm {
    Write-Host '[cdm] clean deploy mode: down -> pull -> build -> up -> life'
    Invoke-Compose -Args @('down')
    Invoke-Compose -Args @('pull')
    Invoke-Compose -Args @('build')
    Invoke-Compose -Args @('up','-d')
    Invoke-Life
}

function Invoke-Doctor {
    Write-Host '[doctor] checking toolchain...'
    try { & docker --version } catch { Write-Host '[doctor] docker not found' }
    try { & docker compose version } catch { Write-Host '[doctor] docker compose not found' }
    Write-Host "[doctor] compose file: $ComposeFile"

    try {
        & docker compose -f $ComposeFile config | Out-Null
        Write-Host '[doctor] compose config valid'
    }
    catch {
        Write-Host '[doctor] compose config has issues'
        throw
    }
}

switch ($Target) {
    'help' { Show-Help }
    'up' { Invoke-Compose -Args @('up','-d') }
    'down' { Invoke-Compose -Args @('down') }
    'stop' { Invoke-Compose -Args @('stop') }
    'start' { Invoke-Compose -Args @('start') }
    'restart' {
        Invoke-Compose -Args @('down')
        Invoke-Compose -Args @('up','-d')
    }
    'build' { Invoke-Compose -Args @('build') }
    'rebuild' { Invoke-Compose -Args @('build','--no-cache') }
    'pull' { Invoke-Compose -Args @('pull') }
    'ps' { Invoke-Compose -Args @('ps') }
    'logs' { Invoke-Compose -Args @('logs','-f','--tail=200') }
    'life' { Invoke-Life }
    'cdm' { Invoke-Cdm }
    'end2end' { Invoke-Cdm }
    'doctor' { Invoke-Doctor }
    'airflow' { Invoke-Compose -Args @('exec','airflow','airflow','dags','list') }
    'init-db' { Invoke-Compose -Args @('exec','postgres','psql','-U','$env:POSTGRES_USER','-d','$env:POSTGRES_DB','-f','/docker-entrypoint-initdb.d/01-timescale.sql') }
    'seed-neo' { Invoke-Compose -Args @('exec','neo4j','cypher-shell','-u','$env:NEO4J_USER','-p','$env:NEO4J_PASSWORD','-f','/opt/neo4j/import/ontologies.cypher') }
    'fabric-up' { & docker compose -f 'docker-compose.clx.fabric.yml' up -d }
    'fabric-down' { & docker compose -f 'docker-compose.clx.fabric.yml' down }
    default { Show-Help }
}
