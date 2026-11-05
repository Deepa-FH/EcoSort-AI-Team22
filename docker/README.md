# Docker instructions

The application runs in a Linux CPU container. The LLM API key is injected at runtime through `LLM_API_KEY`; it is not copied into the image. The YOLO checkpoint is mounted from the host `models` folder.

## Requirements

- Docker Desktop running.
- The trained checkpoint at `../models/best_model.pt` relative to this folder.

## Build the image

Run these commands from the project root, not from inside `docker`:

```powershell
cd "C:\Users\asus\Desktop\FH Dortmund\Python Compact Programming\Project waste detection\Final Project submission\final project"
docker build -f docker\Dockerfile -t ecosort-ai:latest .
```

## Run with an API key

PowerShell:

```powershell
$env:LLM_API_KEY="YOUR_API_KEY"
docker run --rm --name ecosort-ai `
  -p 8501:8501 `
  -e LLM_API_KEY `
  -v "${PWD}\models:/app/models:ro" `
  ecosort-ai:latest
```

Open `http://127.0.0.1:8501`.

The model must exist at `models\best_model.pt`. If the model has a different filename or location, change the volume and add a matching command:

```powershell
docker run --rm -p 8501:8501 -e LLM_API_KEY `
  -v "C:\path\to\model-folder:/app/models:ro" `
  ecosort-ai:latest
```

## Run with Docker Compose

From the project root:

```powershell
$env:LLM_API_KEY="YOUR_API_KEY"
docker compose -f docker\compose.yml up --build
```

Stop it with `Ctrl+C`, or run `docker compose -f docker\compose.yml down` in another terminal.

## Other OpenAI-compatible providers

```powershell
$env:LLM_API_KEY="YOUR_API_KEY"
$env:LLM_MODEL="YOUR_MODEL"
$env:LLM_BASE_URL="https://your-provider.example/v1"
docker compose -f docker\compose.yml up --build
```

Never place the API key in the Dockerfile, source code, `compose.yml`, or Git.
