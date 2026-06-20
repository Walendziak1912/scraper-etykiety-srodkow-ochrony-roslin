# UV Installer
# Requires -RunAsAdministrator
#.\UV-INSTALLER.ps1 -InstallDir "D:\Program_Files\UV" -AddToPath

param(
    [string]$InstallDir = "C:\Program_Files\UV",
    [switch]$AddToPath = $true
)

Write-Host ""
Write-Host "========================================="
Write-Host "           UV Installer (Windows)"
Write-Host "========================================="
Write-Host ""

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$windowsIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$windowsPrincipal = New-Object Security.Principal.WindowsPrincipal($windowsIdentity)
$adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
$hasPlaywrightBrowsers = $false

if (-not ($windowsPrincipal.IsInRole($adminRole))) {
    Write-Host "ERROR: This script must be run with Administrator privileges" -ForegroundColor Red
    exit 1
}

$possiblePaths = @(
    "$env:USERPROFILE\.local\bin\uv.exe",
    "$env:LOCALAPPDATA\uv\bin\uv.exe",
    "$InstallDir\uv.exe"
)

$uvCmd = Get-Command uv -ErrorAction SilentlyContinue

if ($uvCmd) {
    Write-Host "[UV] UV is already installed on this system!" -ForegroundColor Yellow
    Write-Host "[UV] Found at: $($uvCmd.Source)"
    
    Write-Host "[UV] Testing existing UV installation..." -ForegroundColor Cyan

    try {
        $existingVersion = & $uvCmd.Source --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "UV executable exists but failed to run!"
            exit 1
        }
        Write-Host "[UV] UV works version: $existingVersion" -ForegroundColor Green
    }
    catch {
        Write-Error "UV executable exists but is invalid/corrupted!"
        exit 1
    }

    return
}

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        Write-Host "[UV] UV is already installed at: $path" -ForegroundColor Yellow
        return
    }
}

Write-Host "[UV] Fetching release 0.9.10" -ForegroundColor Cyan

$browser_download_url_zip = "https://github.com/astral-sh/uv/releases/download/0.9.10/uv-x86_64-pc-windows-msvc.zip"
$browser_download_url_sha = "https://github.com/astral-sh/uv/releases/download/0.9.10/uv-x86_64-pc-windows-msvc.zip.sha256"

$assetName = Split-Path $browser_download_url_zip -Leaf
$shaAssetName = Split-Path $browser_download_url_sha -Leaf

Write-Host "[UV] Found asset: $($assetName)"

if (-not (Test-Path $InstallDir)) {
    Write-Host "[UV] Creating install directory: $InstallDir"
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

$tempZip = Join-Path $env:TEMP $assetName
$tempSha = Join-Path $env:TEMP $shaAssetName

Write-Host "[UV] Temporary download path: $tempZip"
Write-Host "[UV] Temporary SHA256 path: $tempSha"

Write-Host "[UV] Downloading binary..."
Invoke-WebRequest -Uri $browser_download_url_zip -OutFile $tempZip -UseBasicParsing

Write-Host "[UV] Downloading SHA256..."
Invoke-WebRequest -Uri $browser_download_url_sha -OutFile $tempSha -UseBasicParsing

Write-Host "[UV] Validating checksum..."
$fileHash = (Get-FileHash -Path $tempZip -Algorithm SHA256).Hash.ToLower()
$expectedHash = (Get-Content $tempSha).Split(" ")[0].ToLower()

if ($fileHash -ne $expectedHash) {
    Write-Error "SHA256 mismatch! Aborting."
    exit 1
}

Write-Host "[UV] Checksum OK" -ForegroundColor Green

Write-Host "[UV] Extracting..."
Expand-Archive -Path $tempZip -DestinationPath $InstallDir -Force

$binPath = Join-Path $InstallDir "uv.exe"
if (-not (Test-Path $binPath)) {
    Write-Error "Extraction failed � uv.exe not found"
    exit 1
}

if ($AddToPath) {
    Write-Host "[UV] Adding to PATH..."

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

    if ($currentPath -notlike "*${InstallDir}*") {
        $newPath = $currentPath + ";" + $InstallDir
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "[UV] Added to system PATH" -ForegroundColor Green
    } else {
        Write-Host "[UV] Already in PATH"
    }
}

Write-Host "[UV] Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "         UV has been installed!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
