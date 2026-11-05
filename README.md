# EcoSort AI Waste Sorting and Recycling Assistant

This is the full four-subsystem Flask dashboard for the Python Compact Programming capstone project. It preserves the working dashboard behavior: login, signup, camera/upload analysis, configurable confidence threshold, local YOLO predictions, colour-coded recycling rules, scan history, dashboard statistics, editable administrator rules, and chat. It uses an OpenAI-compatible LLM API for explanations; the Codex-specific integration has been removed.

## Run the complete project

1. Create an environment: `python -m venv .venv` and activate it.
2. Install packages: `python -m pip install -r requirements.txt`.
3. Put the trained checkpoint at `models/best_model.pt`, or pass `--model PATH`.
4. Supply the LLM key without committing it:

```powershell
$env:LLM_API_KEY="your-key"
python main.py --model models\best_model.pt
```

Alternatively: `python main.py --api-key "your-key" --llm-model "gpt-4o-mini" --llm-base-url "https://api.openai.com/v1"`.

The app opens at `http://127.0.0.1:5000`. Sign in with the development account `admin` / `admin`. API keys are never stored in source code. If the LLM is unavailable, local YOLO results and local recycling rules still work; chat and low-confidence review return an error until the API is available.

The app stores `sortly.sqlite3` and captured photos in the project folder by default. If Windows permissions restrict that folder, set `SORTLY_DATA_DIR` to a writable folder before starting.

## Team responsibilities

1. Dataset and preprocessing: `dataset_preprocessing/`.
2. AI image recognition: `image_recognition/`.
3. Recycling rules and Ask AI: `recycling_ai/`.
4. Web dashboard and integration: `web_dashboard/`.

Every team member owns at least three unique classes. See `diagrams/` and the final presentation PDF for the UML and speaking notes.

## Test

Run `python -m pytest -q`. The project includes 15 tests covering validation, recognition data structures, pipeline behavior, rules, API-key errors, fallback behavior, and the LLM path.

## Useful commands

```powershell
python main.py --api-key "your-key" --model models\best_model.pt --port 5000
python main.py --api-key "your-key" --model models\best_model.pt --port 8502 --no-browser
```

## Routes

- `GET /login`: sign in.
- `GET /`: upload and camera dashboard.
- `POST /api/analyze`: multipart field `photo` and optional `threshold`.
- `POST /api/chat`: JSON with `message`, `prediction`, and optional `image_name`.
- `GET /dashboard`: scan statistics.
- `GET /history`: previous scans.
- `GET /admin/rules`: administrator rule editor.
