# UV Uninstaller for Windows (PowerShell 5.1+ compatible)
#.\UV-UNINSTALLER.ps1 -InstallDir "C:\Program_Files\UV"
param(
    [string]$InstallDir = "C:\Program_Files\UV"
)

Write-Host ""
Write-Host "========================================="
Write-Host "           UV Uninstaller (Windows)"
Write-Host "========================================="
Write-Host ""

$windowsIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$windowsPrincipal = New-Object Security.Principal.WindowsPrincipal($windowsIdentity)
$adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
$hasPlaywrightBrowsers = $false

if (-not ($windowsPrincipal.IsInRole($adminRole))) {
    Write-Host "ERROR: This script must be run with Administrator privileges" -ForegroundColor Red
    exit 1
}

function Info($msg)  { Write-Host "[INFO]  $msg"}
function Warn($msg)  { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function ErrorMsg($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$cmd = Get-Command uv -ErrorAction SilentlyContinue
$uvDetected = @()

if ($cmd) {
    $uvDetected += $cmd.Source
}

$possibleLocations = @(
    $uvDetected,
    "$env:USERPROFILE\.local\bin\uv.exe",
    "$env:LOCALAPPDATA\uv\bin\uv.exe",
    "$InstallDir\uv.exe"

) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

if (-not $possibleLocations -or $possibleLocations.Count -eq 0) {
    Warn "UV is not installed on this system."
    Read-Host "Press Enter to exit..."
    exit 0
}

Info "Detected UV installations:"
foreach ($loc in $possibleLocations) {
    Write-Host " - $loc"
}

try {
    $version = (& uv --version 2>$null)
    Info "UV version: $version"
} catch {
    Info "UV version: unknown"
}

Write-Host ""
$confirm = Read-Host "Do you want to uninstall UV? (y/n)"

if ($confirm -notmatch '^(y|yes)$') {
    Info "Uninstall cancelled."
    Read-Host "Press Enter to exit..."
    exit 0
}

Write-Host ""
Info "Starting UV uninstallation..."
Write-Host ""

foreach ($exe in $possibleLocations) {
    if (Test-Path $exe) {
        Info "Removing: $exe"
        try {
            Remove-Item $exe -Force -ErrorAction Stop
        } catch {
            Warn "Unable to remove: $exe (admin rights may be required)"
        }
    }
}

$installFolders = @(
    "C:\Program Files\UV",
    "C:\Program Files\uv",
    "$env:LOCALAPPDATA\uv",
    "$env:LOCALAPPDATA\Programs\uv",
    "$InstallDir"
)

foreach ($folder in $installFolders) {
    if (Test-Path $folder) {
        Info "Removing installation folder: $folder"
        try {
            Remove-Item $folder -Recurse -Force -ErrorAction Stop
        } catch {
            Warn "Unable to remove folder: $folder"
        }
    }
}

$configDirs = @(
    "$env:USERPROFILE\.uv",
    "$env:APPDATA\uv",
    "$env:LOCALAPPDATA\uv-cache",
    "$env:TEMP\uv"
)

foreach ($dir in $configDirs) {
    if (Test-Path $dir) {
        Info "Removing folder: $dir"
        try {
            Remove-Item $dir -Recurse -Force -ErrorAction Stop
        } catch {
            Warn "Unable to remove: $dir"
        }
    }
}

Write-Host ""
Info "Cleaning PATH entries..."

$pathsToRemove = @(
    "$env:USERPROFILE\.local\bin",
    "$env:LOCALAPPDATA\uv\bin",
    "$env:LOCALAPPDATA\Programs\uv"
)

foreach ($scope in @("User", "Machine")) {
    $pathValue = [Environment]::GetEnvironmentVariable("Path", $scope)

    if ($pathValue) {
        $segments = $pathValue -split ";"
        $newSegments = @()

        foreach ($seg in $segments) {
            $shouldRemove = $false
            foreach ($uvPath in $pathsToRemove) {
                if ($seg -eq $uvPath) { 
                    $shouldRemove = $true 
                }
            }

            if (-not $shouldRemove) {
                $newSegments += $seg
            } else {
                Info "Removing PATH entry: $seg"
            }
        }

        $newPath = ($newSegments -join ";")
        [Environment]::SetEnvironmentVariable("Path", $newPath, $scope)
    }
}

Info "Checking for shortcuts..."

$shortcuts = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\uv.lnk",
    "$env:USERPROFILE\Desktop\uv.lnk"
)

foreach ($sc in $shortcuts) {
    if (Test-Path $sc) {
        Info "Removing shortcut: $sc"
        Remove-Item $sc -Force
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "         UV has been Ininstalled!!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

$stillThere = Get-Command uv -ErrorAction SilentlyContinue

if ($stillThere) {
    Warn "UV is still detected: $($stillThere.Source)"
    Warn "Restart your terminal or sign out/in."
} else {
    Info "UV successfully removed."
}

Write-Host ""
Info "Restart PowerShell or log out to refresh PATH."
Read-Host "Press Enter to exit..."
