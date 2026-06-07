$projectRoot = Split-Path -Parent $PSScriptRoot
$launcherScript = Join-Path $projectRoot "build\launch_app.ps1"
$iconPath = Join-Path $projectRoot "assets\icons\app.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Diablo Translator.lnk"

if (-not (Test-Path $launcherScript)) {
    Write-Host "Script introuvable : $launcherScript"
    exit 1
}

if (-not (Test-Path $iconPath)) {
    Write-Host "Icone introuvable, generation..."
    py -3 (Join-Path $projectRoot "assets\icons\generate_app_icon.py")
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$launcherScript`""
$shortcut.WorkingDirectory = $projectRoot
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Diablo Translator - traduction chat live"
$shortcut.Save()

Write-Host "Raccourci cree : $shortcutPath"
Write-Host "Icone HD : $iconPath"
