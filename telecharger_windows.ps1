# Téléchargement Windows officiel en arrière-plan
# Les ISO Microsoft utilisent des liens temporaires générés par leur site (ils ne sont pas
# publiés comme des URL permanentes). Ce script accepte donc un lien ISO direct Microsoft
# ou télécharge l'outil officiel Media Creation Tool si aucun lien direct n'est fourni.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$outDir = Join-Path $root 'downloads'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host 'USB Boot Windows - téléchargement officiel Microsoft' -ForegroundColor Cyan
Write-Host '1 - Windows 11'
Write-Host '2 - Windows 10'
$choice = Read-Host 'Choisissez la version'
if ($choice -eq '1') {
    $version = 'Windows 11'
    $page = 'https://www.microsoft.com/software-download/windows11'
    $tool = 'https://go.microsoft.com/fwlink/?linkid=2156295'
} elseif ($choice -eq '2') {
    $version = 'Windows 10'
    $page = 'https://www.microsoft.com/software-download/windows10'
    $tool = 'https://go.microsoft.com/fwlink/?LinkId=691209'
} else { throw 'Choix invalide.' }

$lang = Read-Host 'Langue (ex: fr-FR, en-US, de-DE)'
if ([string]::IsNullOrWhiteSpace($lang)) { $lang = 'fr-FR' }

Write-Host ''
Write-Host 'Microsoft ne fournit pas de lien ISO permanent : les liens directs expirent.' -ForegroundColor Yellow
Write-Host 'Collez un lien ISO Microsoft temporaire si vous en avez un.'
$url = Read-Host 'Lien ISO direct (laisser vide pour télécharger Media Creation Tool)'

if ([string]::IsNullOrWhiteSpace($url)) {
    $file = Join-Path $outDir (if ($choice -eq '1') { 'MediaCreationTool_Win11.exe' } else { 'MediaCreationTool_Win10.exe' })
    Write-Host "Téléchargement en arrière-plan de l'outil officiel..."
    Start-BitsTransfer -Source $tool -Destination $file -DisplayName "$version - Microsoft Media Creation Tool" -Description "Téléchargement officiel"
    Write-Host "Terminé : $file" -ForegroundColor Green
    Write-Host "Lancez cet outil pour créer une ISO ou une clé USB."
    Start-Process $page
    exit 0
}

$uri = [Uri]$url
if ($uri.Host -notmatch '(^|\.)microsoft\.com$|(^|\.)windows\.net$') {
    throw 'Sécurité : le lien doit provenir de microsoft.com ou windows.net.'
}
$name = Split-Path $uri.AbsolutePath -Leaf
if ([string]::IsNullOrWhiteSpace($name) -or $name -notmatch '\.iso$') { $name = "${version}_${lang}.iso" }
$name = $name -replace '[<>:"/\\|?*]', '_'
$file = Join-Path $outDir $name
Write-Host "Téléchargement ISO en arrière-plan vers $file ..."
Start-BitsTransfer -Source $url -Destination $file -DisplayName "$version $lang - ISO Microsoft" -Description 'Téléchargement ISO officiel'
Write-Host "Terminé : $file" -ForegroundColor Green
Write-Host 'Vous pouvez maintenant sélectionner cette ISO dans usb_boot_windows.py.'
