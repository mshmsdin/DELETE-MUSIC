$ErrorActionPreference = 'Stop'
$sendToDirectory = Join-Path $env:APPDATA 'Microsoft\Windows\SendTo'
@('Remove Background Music.lnk', 'إزالة الموسيقى من الفيديو.lnk') | ForEach-Object {
    Remove-Item -LiteralPath (Join-Path $sendToDirectory $_) -Force -ErrorAction SilentlyContinue
}
Write-Host 'Removed the Remove Music shortcut from Send to. The app files and model were kept.'
