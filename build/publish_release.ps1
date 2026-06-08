# Publie la release GitHub v1.1.0 avec DiabloTranslator.exe
# Prerequis : gh auth login (une seule fois)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Exe = Join-Path $Root "build\dist\DiabloTranslator.exe"
$Notes = Join-Path $Root "build\RELEASE_v1.1.0.md"
$Tag = "v1.1.0"

if (-not (Test-Path $Exe)) {
    Write-Host "Exe introuvable. Lancez d'abord : py -3 build\build.py --clean --shortcut"
    exit 1
}

$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Connectez-vous a GitHub : gh auth login"
    gh auth login
}

Set-Location $Root

if (-not (git tag -l $Tag)) {
    git tag -a $Tag -m "Diablo Translator v1.1.0 — Hub Sanctuaire, Live web, traduction bidirectionnelle"
}

git push origin $Tag

gh release view $Tag *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Release $Tag existe deja — upload de l'asset..."
    gh release upload $Tag $Exe --clobber
} else {
    gh release create $Tag $Exe `
        --title "Diablo Translator v1.1.0" `
        --notes-file $Notes
}

Write-Host ""
Write-Host "Release publiee : https://github.com/wargriff/diablo_translator/releases/tag/$Tag"
