$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ReleaseRoot = Join-Path $Root "release"
$DistApp = Join-Path $ReleaseRoot "Penilaian PIB"

Set-Location $Root

python -m pip install -r requirements.txt
python -m pytest tests/ -v
python -m PyInstaller PenilaianPIB.spec --noconfirm --clean --distpath $ReleaseRoot

New-Item -ItemType Directory -Force -Path (Join-Path $DistApp "assets") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DistApp "data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DistApp "exports") | Out-Null

if (Test-Path (Join-Path $Root "assets\logo.png")) {
    Copy-Item (Join-Path $Root "assets\logo.png") (Join-Path $DistApp "assets\logo.png") -Force
}
if (Test-Path (Join-Path $Root "assets\logo.ico")) {
    Copy-Item (Join-Path $Root "assets\logo.ico") (Join-Path $DistApp "assets\logo.ico") -Force
}

Write-Host ""
Write-Host "Build selesai:"
Write-Host (Join-Path $DistApp "Penilaian PIB.exe")
