$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $appRoot 'RemoveMusic.exe'

if (-not (Test-Path -LiteralPath $launcher)) { throw 'The application launcher is missing. Run install.ps1 first.' }
if (-not (Test-Path -LiteralPath (Join-Path $appRoot '.venv\Scripts\pythonw.exe'))) {
    throw 'The Python environment is unavailable. Run install.ps1 first.'
}

$sendToDirectory = Join-Path $env:APPDATA 'Microsoft\Windows\SendTo'
if (-not (Test-Path -LiteralPath $sendToDirectory)) {
    New-Item -ItemType Directory -Path $sendToDirectory -Force | Out-Null
}
$culture = (Get-Culture).Name
$shortcutName = if ($culture -like 'ar*') { 'إزالة الموسيقى من الفيديو.lnk' } else { 'Remove Background Music.lnk' }
$sendToLink = Join-Path $sendToDirectory $shortcutName
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($sendToLink)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $appRoot
$shortcut.IconLocation = "$launcher,0"
$shortcut.Description = 'Create a copy of the video without background music'
$shortcut.Save()

Write-Host "Added '$shortcutName' under Send to."
