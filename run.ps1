param(
    [string]$ApiKey = $env:LLM_API_KEY,
    [string]$Model = "models\best_model.pt",
    [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectRoot

$ProjectPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$TrainingPython = "C:\Users\asus\Documents\ChatGPT\AI Powered waste sorting and recycling assistance\.venv-training\Scripts\python.exe"

if (Test-Path -LiteralPath $ProjectPython) {
    $Python = $ProjectPython
} elseif (Test-Path -LiteralPath $TrainingPython) {
    $Python = $TrainingPython
} else {
    throw "Python 3.12 environment not found. Create .venv with Python 3.12 and install requirements.txt."
}

$ModelPath = if ([IO.Path]::IsPathRooted($Model)) { $Model } else { Join-Path $ProjectRoot $Model }
if (-not (Test-Path -LiteralPath $ModelPath)) {
    throw "Model not found: $ModelPath"
}

$DataPath = Join-Path $ProjectRoot "data"
New-Item -ItemType Directory -Force -Path $DataPath | Out-Null
$env:SORTLY_DATA_DIR = $DataPath

if ($ApiKey) {
    $env:LLM_API_KEY = $ApiKey
} else {
    Write-Warning "No API key supplied. Image recognition works, but Ask AI will be unavailable."
}

Write-Host "Starting EcoSort AI at http://127.0.0.1:$Port/login" -ForegroundColor Green
Write-Host "Keep this window open. Press Ctrl+C to stop the server." -ForegroundColor Yellow

& $Python -u main.py --model $ModelPath --host 127.0.0.1 --port $Port
