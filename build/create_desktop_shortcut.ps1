$projectRoot = Split-Path -Parent $PSScriptRoot
$distExe = Join-Path $projectRoot "build\dist\DiabloTranslator.exe"
$launchScript = Join-Path $projectRoot "build\launch_app.ps1"
$iconPath = Join-Path $projectRoot "assets\icons\app.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Diablo Translator.lnk"

if (-not (Test-Path $iconPath)) {
    Write-Host "Icone introuvable, generation..."
    py -3 (Join-Path $projectRoot "assets\icons\generate_app_icon.py")
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)

if (Test-Path $distExe) {
    $shortcut.TargetPath = $distExe
    $shortcut.WorkingDirectory = Split-Path $distExe
    $shortcut.Arguments = ""
} else {
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$launchScript`""
    $shortcut.WorkingDirectory = $projectRoot
}

$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Diablo Translator - traduction chat live Diablo III / IV"
$shortcut.Save()

Write-Host "Raccourci cree : $shortcutPath"
if (Test-Path $distExe) {
    Write-Host "Cible : $distExe"
} else {
    Write-Host "Cible : Python (Build-Pro.bat pour creer l exe)"
}
