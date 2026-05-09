<#
.SYNOPSIS
	Quick recovery helper for the Kloud backend stack when running on Windows.

.DESCRIPTION
	Stops residual Python and Node processes, clears transient build artefacts,
	and rehydrates the virtual environment + npm workspaces. Use when a local
	demo environment becomes unstable after interrupted builds.
#>

param(
	[switch]$DeepClean
)

Write-Host "[Kloud] Fix script started..." -ForegroundColor Cyan

# Stop stray processes that often lock ports.
Get-Process python, node -ErrorAction SilentlyContinue |
	ForEach-Object {
		Write-Host "Stopping process $($_.ProcessName) (PID $($_.Id))" -ForegroundColor Yellow
		$_ | Stop-Process -Force -ErrorAction SilentlyContinue
	}

# Jump to repo root
$repoRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $repoRoot

if ($DeepClean) {
	Write-Host "Performing deep clean (node_modules, .next, dist)" -ForegroundColor Yellow
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
		"node_modules", "apps\web\node_modules", "apps\web\.next", "apps\api\__pycache__"
}

Write-Host "Restoring Python dependencies" -ForegroundColor Cyan
$requirements = Join-Path $repoRoot 'requirements.txt'
if (Test-Path $requirements) {
	& "$repoRoot\.venv\Scripts\python.exe" -m pip install -r $requirements 2>$null
} else {
	& "$repoRoot\.venv\Scripts\python.exe" -m pip install -e . 2>$null
}

Write-Host "Restoring npm workspaces" -ForegroundColor Cyan
npm install | Out-Null

Write-Host "Fix script complete. Run 'npm run dev' or 'scripts\start-all.ps1' to relaunch." -ForegroundColor Green


