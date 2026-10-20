$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $appRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $launcher) { throw 'Python 3.10 is required. Install Python 3.10 from python.org, then run this script again.' }
    & py -3.10 -m venv (Join-Path $appRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the isolated Python environment.' }
}

& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Could not update pip.' }

$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
$useNvidia = $false
if ($nvidiaSmi) {
    & $nvidiaSmi.Source --query-gpu=name --format=csv,noheader *> $null
    $useNvidia = $LASTEXITCODE -eq 0
}

if ($useNvidia) {
    Write-Host 'NVIDIA GPU detected. Installing the CUDA-enabled runtime.' -ForegroundColor Cyan
    & $python -m pip install 'torch==2.8.0+cu128' 'torchvision==0.23.0+cu128' --index-url 'https://download.pytorch.org/whl/cu128'
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the CUDA-enabled PyTorch runtime.' }
    & $python -m pip install 'audio-separator[gpu]' 'onnxruntime-gpu[cuda,cudnn]' imageio-ffmpeg Pillow
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the NVIDIA GPU audio runtime.' }
}
else {
    Write-Host 'No NVIDIA GPU detected. Installing the CPU runtime; processing will be slower.' -ForegroundColor Yellow
    & $python -m pip install 'torch==2.8.0+cpu' 'torchvision==0.23.0+cpu' --index-url 'https://download.pytorch.org/whl/cpu'
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the CPU PyTorch runtime.' }
    & $python -m pip install 'audio-separator[cpu]' onnxruntime imageio-ffmpeg Pillow
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the CPU audio runtime.' }
}

$modelDir = Join-Path $appRoot 'models'
New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
& (Join-Path $appRoot '.venv\Scripts\audio-separator.exe') --download_model_only --model_filename 'UVR_MDXNET_KARA_2.onnx' --model_file_dir $modelDir
if ($LASTEXITCODE -ne 0) { throw 'Could not download the speech separation model.' }

& (Join-Path $appRoot 'build_launcher.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Could not build the Windows launcher.' }
& (Join-Path $appRoot 'register_context_menu.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Could not register the Send To shortcut.' }

Write-Host 'Installation complete. Select a video, then use Send to > Remove Background Music.' -ForegroundColor Green
