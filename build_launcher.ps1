$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler)) { throw 'The Windows C# compiler is unavailable.' }
$source = Join-Path $appRoot 'RemoveMusicLauncher.cs'
$output = Join-Path $appRoot 'RemoveMusic.exe'
$icon = Join-Path $appRoot 'music_off.ico'
if (-not (Test-Path -LiteralPath $icon)) {
    $python = Join-Path $appRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) { throw 'The Python environment is unavailable. Run install.ps1 first.' }
    & $python (Join-Path $appRoot 'build_icon.py')
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $icon)) { throw 'Could not create the application icon.' }
}
& $compiler /nologo /target:winexe /platform:x64 /reference:System.Windows.Forms.dll "/win32icon:$icon" "/out:$output" $source
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $output)) { throw 'Could not build the launcher.' }
Write-Host "Built $output"
