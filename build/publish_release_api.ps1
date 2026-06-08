# Publie release v1.1.0 via API GitHub (utilise les identifiants git locaux)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Exe = Join-Path $Root "build\dist\DiabloTranslator.exe"
$NotesFile = Join-Path $Root "build\RELEASE_v1.1.0.md"
$Tag = "v1.1.0"
$Repo = "wargriff/diablo_translator"

if (-not (Test-Path $Exe)) {
    throw "Exe introuvable : $Exe"
}

$cred = "protocol=https`nhost=github.com`n`n"
$filled = ($cred | git credential fill 2>$null) -join "`n"
if ($filled -notmatch 'password=(.+)') {
    throw "Token GitHub introuvable. Configurez git credential ou GH_TOKEN."
}
$token = $Matches[1].Trim()
$headers = @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

function Get-ReleaseByTag {
    try {
        return Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/tags/$Tag" -Headers $headers
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 404) { return $null }
        throw
    }
}

$release = Get-ReleaseByTag
if (-not $release) {
    $notes = [System.IO.File]::ReadAllText($NotesFile, [System.Text.Encoding]::UTF8)
    $notesJson = ConvertTo-Json -InputObject $notes -Compress
    $body = "{`"tag_name`":`"$Tag`",`"name`":`"Diablo Translator v1.1.0`",`"body`":$notesJson,`"draft`":false,`"prerelease`":false}"
    $release = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$Repo/releases" -Headers $headers -Body $body -ContentType "application/json; charset=utf-8"
    Write-Host "Release creee : $($release.html_url)"
} else {
    Write-Host "Release existante : $($release.html_url)"
}

$assetName = "DiabloTranslator.exe"
$existing = @($release.assets) | Where-Object { $_.name -eq $assetName }
foreach ($asset in $existing) {
    Invoke-RestMethod -Method Delete -Uri "https://api.github.com/repos/$Repo/releases/assets/$($asset.id)" -Headers $headers | Out-Null
    Write-Host "Ancien asset supprime : $assetName"
}

$uploadUrl = ($release.upload_url -replace '\{.*$', "") + "?name=$assetName"
$uploadHeaders = @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github+json"
    "Content-Type" = "application/octet-stream"
}
Invoke-RestMethod -Method Post -Uri $uploadUrl -Headers $uploadHeaders -InFile $Exe | Out-Null
$sizeMb = [math]::Round((Get-Item $Exe).Length / 1MB, 1)
Write-Host "Asset uploade : $assetName (${sizeMb} MB)"
Write-Host "URL : $($release.html_url)"
