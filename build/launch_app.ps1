# Lance Diablo Translator — debloque MOTW / SmartScreen pour build local.
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $projectRoot "build\dist"
$exePath = Join-Path $distDir "DiabloTranslator.exe"
$launcher = Join-Path $projectRoot "launcher.py"
$securityScript = Join-Path $projectRoot "build\windows_security.ps1"

function Clear-Motw {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Unblock-File -LiteralPath $Path -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath "$Path`:Zone.Identifier" -Force -ErrorAction SilentlyContinue
}

function Clear-DistMotw {
    if (-not (Test-Path -LiteralPath $distDir)) {
        return
    }

    Get-ChildItem -LiteralPath $distDir -Recurse -File | ForEach-Object {
        Clear-Motw $_.FullName
    }
}

function Start-PythonApp {
    Set-Location $projectRoot

    if (Get-Command py -ErrorAction SilentlyContinue) {
        Start-Process py -ArgumentList "-3", "launcher.py", "gui" -WorkingDirectory $projectRoot
        return
    }

    if (Get-Command pythonw -ErrorAction SilentlyContinue) {
        Start-Process pythonw -ArgumentList "launcher.py", "gui" -WorkingDirectory $projectRoot
        return
    }

    Start-Process python -ArgumentList "launcher.py", "gui" -WorkingDirectory $projectRoot
}

if (Test-Path -LiteralPath $securityScript) {
    powershell -NoProfile -ExecutionPolicy Bypass -File $securityScript -DistPath $distDir | Out-Null
} else {
    Clear-DistMotw
}

Clear-Motw $exePath

if (Test-Path -LiteralPath $exePath) {
    try {
        Start-Process -FilePath $exePath -WorkingDirectory $distDir
        exit 0
    } catch {
        Write-Host "Lancement .exe impossible, bascule vers Python..."
    }
}

if (-not (Test-Path -LiteralPath $launcher)) {
    Write-Host "Erreur : launcher.py introuvable dans $projectRoot"
    exit 1
}

Start-PythonApp
