param([string]$ApiKey = $env:LLM_API_KEY, [string]$Model = "models/best_model.pt")
if (-not $ApiKey) { Write-Error "Pass -ApiKey or set LLM_API_KEY"; exit 1 }
python main.py --api-key $ApiKey --model $Model
