$projectRoot = Split-Path -Parent $PSScriptRoot
$exePath = Join-Path $projectRoot "build\dist\DiabloTranslator.exe"
$iconPath = Join-Path $projectRoot "assets\icons\app.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Diablo Translator.lnk"

if (-not (Test-Path $exePath)) {
    Write-Host "Executable introuvable : $exePath"
    Write-Host "Lancez d'abord : python build/build.py"
    exit 1
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = Split-Path $exePath
$shortcut.IconLocation = if (Test-Path $iconPath) { "$iconPath,0" } else { "$exePath,0" }
$shortcut.Description = "Diablo Translator - traduction chat live"
$shortcut.Save()

Write-Host "Raccourci cree : $shortcutPath"
