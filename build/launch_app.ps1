# Lance Diablo Translator en contournant le blocage Windows (Smart App Control / SmartScreen).
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$exePath = Join-Path $projectRoot "build\dist\DiabloTranslator.exe"
$launcher = Join-Path $projectRoot "launcher.py"

function Remove-MotwBlock {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return
    }

    Unblock-File -Path $Path -ErrorAction SilentlyContinue
    cmd /c "echo.>""$Path`:Zone.Identifier""" 2>$null | Out-Null
    Remove-Item -LiteralPath "$Path`:Zone.Identifier" -Force -ErrorAction SilentlyContinue
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

Remove-MotwBlock $exePath

if (Test-Path $exePath) {
    try {
        Start-Process -FilePath $exePath -WorkingDirectory (Split-Path $exePath)
        exit 0
    } catch {
        Write-Host "Lancement .exe impossible, bascule vers Python..."
    }
}

if (-not (Test-Path $launcher)) {
    Write-Host "Erreur : launcher.py introuvable dans $projectRoot"
    exit 1
}

Start-PythonApp
