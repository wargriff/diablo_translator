# Post-build Windows : debloque MOTW / SmartScreen pour build local.
param(
    [Parameter(Mandatory = $true)]
    [string]$DistPath
)

$ErrorActionPreference = "SilentlyContinue"

function Clear-Motw {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Unblock-File -LiteralPath $Path -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath "$Path`:Zone.Identifier" -Force -ErrorAction SilentlyContinue
}

function Clear-MotwRecursive {
    param([string]$Folder)

    if (-not (Test-Path -LiteralPath $Folder)) {
        return
    }

    Get-ChildItem -LiteralPath $Folder -Recurse -File | ForEach-Object {
        Clear-Motw $_.FullName
    }
}

$dist = (Resolve-Path -LiteralPath $DistPath).Path
$exe = Join-Path $dist "DiabloTranslator.exe"

Write-Host "=== Securite Windows (post-build) ==="
Clear-MotwRecursive $dist

if (Test-Path -LiteralPath $exe) {
    Clear-Motw $exe
    Write-Host "[OK] MOTW retire : $exe"
} else {
    Write-Host "[WARN] Exe introuvable : $exe"
    exit 1
}

Write-Host ""
Write-Host "Conseils Smart App Control / Defender :"
Write-Host "  - Build local = pas de telechargement Internet (MOTW retire)."
Write-Host "  - Si Windows bloque encore : clic droit exe > Proprietes > Debloquer."
Write-Host "  - Signature code (certificat) = seule vraie whitelist Smart App Control."
Write-Host "  - Exclusion Defender (admin) : Parametres > Virus > Exclusions > dossier build\dist"
Write-Host ""
exit 0
