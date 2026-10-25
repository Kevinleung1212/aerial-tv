param(
  [string]$TvIp = "",
  [string]$ApkPath = "",
  [switch]$Install,
  [string]$Adb = "adb"
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not (Get-Command $Adb -ErrorAction SilentlyContinue)) {
    throw "ADB not found. Install Google Platform-Tools and add adb.exe to PATH."
}
if ($TvIp) {
    if ($TvIp -notmatch '^[a-zA-Z0-9.:-]+$') { throw "Invalid TV hostname/IP." }
    & $Adb connect $TvIp
    if ($LASTEXITCODE -ne 0) { throw "ADB connect failed or was not authorized." }
}
$devices = @(& $Adb devices | Select-String '\sdevice$')
if ($devices.Count -ne 1) { throw "Expected exactly one authorized ADB target. Check adb devices." }
$api = (& $Adb shell getprop ro.build.version.sdk).Trim()
$release = (& $Adb shell getprop ro.build.version.release).Trim()
$model = (& $Adb shell getprop ro.product.model).Trim()
Write-Host "TV $model / Android $release / API $api"
if (($api -notmatch '^\d+$') -or [int]$api -lt 28 -or [int]$api -gt 34) {
    throw "This script accepts Android 9 to 14 (API 28 to 34) only."
}
if ($Install) {
    if (-not (Test-Path -LiteralPath $ApkPath -PathType Leaf)) { throw "APK missing: $ApkPath" }
    & $Adb install -r (Resolve-Path -LiteralPath $ApkPath).Path
    if ($LASTEXITCODE -ne 0) { throw "Failed to install. Check incompatible signing certificate." }
}
$installed = (& $Adb shell pm path app.orchard.tv)
if ($LASTEXITCODE -ne 0 -or -not ($installed -match '^package:')) {
    throw "Aerial app.orchard.tv is not installed."
}
& $Adb shell am start -W -n app.orchard.tv/.MainActivity
if ($LASTEXITCODE -ne 0) { throw "Cannot launch Aerial MainActivity." }
Start-Sleep -Seconds 8
$running = (& $Adb shell pidof app.orchard.tv)
if (-not $running) { throw "Aerial has no active process. Check the TV logcat." }
$output = Join-Path (Get-Location).Path ('Aerial-Test-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $output | Out-Null
& $Adb logcat -d -b crash -v time > (Join-Path $output 'crashes.txt')
& $Adb shell wm size > (Join-Path $output 'display.txt')
& $Adb shell dumpsys activity activities > (Join-Path $output 'activities.txt')
Write-Host "Aerial opened successfully; process $running; logs: $output"
Write-Host "Please test: glass Dock; all Apps; folders; hidden Apps; CEC HDMI; volume/brightness; QR phone app grid; Hant/Chinese; wallpaper; screensaver; standby/wake; return to stock Home."
Write-Host "This is a start-and-report smoke test, not complete functional certification."
Write-Host "Review logs before sharing them; they may contain device information."
