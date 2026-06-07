# Debloque MOTW sur site-packages Python avant PyInstaller (Smart App Control).
param(
    [string]$PythonExe = "py"
)

$ErrorActionPreference = "SilentlyContinue"

function Get-SitePackagesPath {
    param([string]$Launcher)

    $output = & $Launcher -3 -c "import site; paths=[p for p in site.getsitepackages() if 'site-packages' in p.lower()]; print(paths[0] if paths else '')" 2>$null
    return ($output | Out-String).Trim()
}

$site = Get-SitePackagesPath -Launcher $PythonExe
if (-not $site -or -not (Test-Path -LiteralPath $site)) {
    Write-Host "[WARN] site-packages introuvable - etape ignoree"
    exit 0
}

Write-Host "=== Deblocage environnement Python (pre-build) ==="
Write-Host "Dossier : $site"

$patterns = @("*.dll", "*.pyd", "*.exe")
$count = 0

foreach ($pattern in $patterns) {
    Get-ChildItem -LiteralPath $site -Recurse -File -Filter $pattern | ForEach-Object {
        Unblock-File -LiteralPath $_.FullName -ErrorAction SilentlyContinue
        $zoneId = "$($_.FullName):Zone.Identifier"
        Remove-Item -LiteralPath $zoneId -Force -ErrorAction SilentlyContinue
        $count++
    }
}

Write-Host "[OK] $count fichiers debloques (MOTW)"
exit 0
