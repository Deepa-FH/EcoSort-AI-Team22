# EcoSort AI - AI-Powered Waste Sorting & Recycling Assistance

Python Compact Programming capstone · **Group 22** · FH Dortmund

Upload or photograph a waste item → a trained **YOLO** model recognises it → local **German bin rules** (and an optional **AI assistant**) tell you where it goes → every scan lands in a **history and dashboard**.

| Team member | Matr. no. | Subsystem | Folder |
|---|---|---|---|
| **Deepa Halapeti** | 7225894 | 1 · Dataset & Preprocessing | [`subsystem_1_dataset_preprocessing/`](subsystem_1_dataset_preprocessing/README.md) |
| **Prasad Hule** | 7225861 | 2 · AI Image Recognition | [`subsystem_2_image_recognition/`](subsystem_2_image_recognition/README.md) |
| **Mayuresh Kumbhar** | 7226310 | 3 · Recycling Rules & Ask AI | [`subsystem_3_recycling_ai/`](subsystem_3_recycling_ai/README.md) |
| **Vijay Kathiresan** | 7226794 | 4 · Web App, Dashboard & Integration | [`subsystem_4_web_integration/`](subsystem_4_web_integration/README.md) |

Each subsystem folder has its own README with the classes, UML diagram, data storage, covered requirements, a live demo command and debugging tips. Presenters: see [`PRESENTATION_GUIDE.md`](PRESENTATION_GUIDE.md).

---

## 1 · Quick start

### ⭐ Easiest: run with Docker (nothing to install except Docker)

The ready-made image is on Docker Hub: **`prasadhule001/ecosort-ai`**. No Python, no packages, no model download.

**Before you start:** install **Docker Desktop** (free): <https://www.docker.com/products/docker-desktop> - open it and wait until it says **"Engine running"**. You also need an **LLM API key** (the key your teacher / KIconnect gave you).

| Step | What to do | Command |
|:-:|---|---|
| 1 | Open a terminal (Windows: **PowerShell**; macOS/Linux: **Terminal**) | |
| 2 | Download the image (about 0.6 GB, once) | `docker pull prasadhule001/ecosort-ai:1.0` |
| 3 | Start it and **pass your API key** | see below |
| 4 | Open the app in your browser | <http://localhost:5000> |
| 5 | Sign in | **Sign in as: Administrator** · username `admin` · password `admin` |
| 6 | Stop the app | press `Ctrl + C` in the terminal |

**Step 3 - start the container and pass the API key** (replace `YOUR_API_KEY` with your real key, keep the quotes):

```powershell
# Windows PowerShell / macOS / Linux - the key is passed with  -e LLM_API_KEY=...
docker run --rm -p 5000:5000 -e LLM_API_KEY="YOUR_API_KEY" prasadhule001/ecosort-ai:1.0
```

Alternative - pass the key as a program argument (same result):

```powershell
docker run --rm -p 5000:5000 prasadhule001/ecosort-ai:1.0 --api-key "YOUR_API_KEY"
```

> **Where does the API key go?** Only in the `docker run` command, at the moment you start the container. It is **not** stored in the image, so everyone can use the same image with their own key.

**Check that it works**
1. In the terminal you should see `'api_key': 'set'` and `Running on http://0.0.0.0:5000`. (`'api_key': 'missing'` = the key was not passed.)
2. In the browser the top bar shows **"Ask AI ready"** (green). **"Local rules mode"** (orange) means no key was received.
3. Upload a photo on the Assistant page → you get the waste type, confidence and the right bin.
4. Raise the threshold to 95 % in *Settings* and upload again → the AI reviews the photo (this proves your key works).

**Useful variations**

| Need | Command |
|---|---|
| Port 5000 already used | `docker run --rm -p 8080:5000 -e LLM_API_KEY="YOUR_API_KEY" prasadhule001/ecosort-ai:1.0` → open <http://localhost:8080> |
| Keep history between runs | add `-v ecosort-data:/data` after `-p 5000:5000` |
| Run in the background | replace `--rm` with `-d --name ecosort` (stop with `docker stop ecosort`) |
| Run the automated tests inside the container | `docker run --rm --entrypoint python prasadhule001/ecosort-ai:1.0 testing.py --quick` |
| No internet / Docker Hub blocked | get `ecosort-ai.tar`, then `docker load -i ecosort-ai.tar` and run with the image name `ecosort-ai` instead of `prasadhule001/ecosort-ai:1.0` |
| Build the image yourself from this folder | `docker build -t ecosort-ai .` then `docker run --rm -p 5000:5000 -e LLM_API_KEY="YOUR_API_KEY" ecosort-ai` |
| Use docker compose | copy `.env.example` to `.env`, put the key in it, run `docker compose up --build` |

**Troubleshooting**

| Problem | Fix |
|---|---|
| `failed to connect to the docker API` | Docker Desktop is not running - start it and wait for "Engine running" |
| `pull access denied` / `insufficient_scope` | Check the spelling `prasadhule001/ecosort-ai:1.0` (lowercase); the repository must be public |
| `port is already allocated` | use `-p 8080:5000` and open port 8080 |
| Page does not open | wait ~20 s after start; check `http://localhost:5000/health` shows `"status":"ok"` |
| "Local rules mode" although you passed a key | the key was empty - check the quotes and spelling (`LLM_API_KEY`) |
| AI answers fail but key is set | no internet, wrong key, or wrong model/URL (`-e LLM_MODEL=...`, `-e LLM_BASE_URL=...`) |
| Apple-Silicon Mac warns about platform | the image is built for Intel/AMD (amd64) and runs through emulation - slower but works |

Notes: the image is CPU-only (works on every laptop, no GPU needed); the "Go live" public-tunnel feature is disabled inside Docker; the camera button needs `localhost` or HTTPS (uploading a photo always works).

---

### Alternative: run with Python (no Docker)

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py --api-key YOUR_API_KEY
```

The browser opens at <http://127.0.0.1:5000>. **Sign in with `admin` / `admin`** (demo account) and choose **Sign in as: Administrator** on the login form.

Where does the API key go? Either of these - never into the source code:

| Way | Command |
|---|---|
| Command-line option | `python main.py --api-key YOUR_API_KEY` |
| Environment variable | PowerShell: `$env:LLM_API_KEY="YOUR_API_KEY"; python main.py` · bash: `LLM_API_KEY=YOUR_API_KEY python main.py` |

Other options: `--port 8000`, `--no-browser`, `--model path/to/best_model.pt`, `--llm-model NAME`, `--llm-base-url URL`, `--data-dir DIR`, `--help`.
Default LLM: KIconnect NRW (`https://chat.kiconnect.nrw/api/v1`, model `mistralai-mistral-small-4`); any OpenAI-compatible API works via `--llm-base-url` / `--llm-model`.

**No key?** The app still runs: recognition and local rules work offline; low-confidence photos get the local rule instead of an AI review, and chat shows how to add a key.

---

## 2 · Automated tests

```bash
python testing.py            # all suites + real-model end-to-end test  (54 tests)
python testing.py --quick    # skip the real YOLO model
python testing.py --live YOUR_API_KEY   # additionally call the real LLM once
python testing.py -v         # list every test
```

Output is one table per team member:

```
[PASS] Subsystem 1 - Dataset & Preprocessing      Deepa Halapeti     13 passed
[PASS] Subsystem 2 - Image Recognition            Prasad Hule        11 passed
[PASS] Subsystem 3 - Recycling Rules & Ask AI     Mayuresh Kumbhar   11 passed
[PASS] Subsystem 4 - Web App & Integration        Vijay Kathiresan   16 passed
[PASS] End-to-end (real YOLO model)               whole team          3 passed
```

The normal tests use a *fake detector* and a *fake LLM* (dependency injection), so they need no GPU, key or internet. Raw pytest also works: `python -m pytest -v`.

Per-member live demos (no web server needed):

```bash
python -m subsystem_1_dataset_preprocessing.demo
python -m subsystem_2_image_recognition.demo
python -m subsystem_3_recycling_ai.demo [--api-key KEY]
```

---

## 3 · Project structure

```
EcoSort_AI_Final/
├── main.py                      entry point  (python main.py --api-key KEY)
├── testing.py                   automated test runner
├── Dockerfile · docker-compose.yml · .env.example · requirements.txt
├── models/best_model.pt         trained YOLO weights (7 classes)
├── sample_data/                 18 labelled demo photos
├── shared/                      EcoSortError + BaseErrorHandler (inherited by every subsystem)
├── subsystem_1_dataset_preprocessing/   Deepa   - validate, preprocess, dataset tools
├── subsystem_2_image_recognition/       Prasad  - YOLO detection, confidence, evaluation
├── subsystem_3_recycling_ai/            Mayuresh- rules, prompts, LLM client, fallback
├── subsystem_4_web_integration/         Vijay   - Flask app, SQLite, auth, dashboard, wiring
├── templates/ · static/         glassmorphism UI (HTML, CSS, JS) for desktop & phone
├── tests/                       one test file per subsystem + end-to-end
└── diagrams/                    architecture + UML overview
```

### How the pieces fit

```mermaid
flowchart LR
  U[User photo] --> V[S1 ImageValidator]
  V --> P[S1 PreprocessingPipeline]
  P --> R[S2 ImageRecognitionService / YOLO]
  R -->|confident| G[S3 RecyclingRuleEngine]
  R -->|unsure| A[S3 WasteAssistant -> LLM or local fallback]
  G --> W[S4 ScanService + SQLite]
  A --> W
  W --> D[S4 Dashboard / History / CSV]
```

Full UML: [`diagrams/architecture.md`](diagrams/architecture.md).

## 4 · OOP concepts demonstrated (and where)

| Concept | Example |
|---|---|
| Classes, `__init__`, attributes | every class; e.g. `ImageValidator.__init__` |
| Encapsulation (private `_x`, properties with validation) | `ImageValidator.max_bytes`, `ConfidenceFilter.threshold` |
| Getters/setters (Pythonic + UML style) | `DatasetMetadata` (`version` and `getVersion()/setVersion()`) |
| Inheritance | `EcoSortError` → per-subsystem errors; `BaseErrorHandler` → 4 handlers; `ImageStep` → steps |
| Abstract base class | `ImageStep` (`@abstractmethod apply`) |
| Polymorphism / protocols | `RuleStore` (in-memory store vs SQLite `WasteRepository`) |
| Operator overloading | `RGBStep() \| ResizeStep(320)` builds a pipeline (`__or__`) |
| Composition & dependency injection | `WasteAssistant(rules, llm, prompts)`, `create_application(config, detector, llm)` |
| Dataclasses / immutable value objects | `Detection`, `PredictionResult`, `RecyclingRule`, `GuidanceResponse` |
| Iterator / generator | `DetectionStream`, `ConfidenceFilter.filter` |
| Class/static methods | `AppConfig.from_cli`, `PreprocessingPipeline.default` |
| Exception chaining | `raise InferenceError(...) from error` |
| Repository / facade patterns | `WasteRepository`, `IntegrationController`, `DatasetManager` |

## 5 · Data storage

SQLite file `data/sortly.sqlite3` (tables `users`, `rules`, `scans`, `usage_events`) + photos in `data/camera_captures/`. In Docker this folder is `/data` (use a volume to keep it).

## 6 · Roles and permissions

Choose **Sign in as** on the login form (the choice must match the account's role). Accounts are created on the sign-up page (invitation code `pythonai`).

| Feature | Normal user | Municipality worker | Administrator |
|---|:-:|:-:|:-:|
| Assistant (photo scan, chat), Settings (threshold default **65 %**) | yes | yes | yes |
| Dashboard (charts, filters) | - | yes | yes |
| Scan history, CSV export | - | - | yes |
| Edit waste rules | - | - | yes |
| "Go live" public tunnel (local Python only) | - | - | yes |

## 7 · Good to know

* **Security:** passwords are hashed; uploads are validated and size-limited (8 MB); API errors never expose stack traces; the API key is never logged or sent to the browser. The default `admin/admin` account and sign-up code `pythonai` are for demonstration - change with `SORTLY_USERNAME`, `SORTLY_PASSWORD`, `SORTLY_SIGNUP_CODE`.
* **Public link ("Go live")**: only when running with Python on a PC that has `cloudflared` installed (Settings → Go live). Disabled in Docker (`--no-tunnel` disables it anywhere).
* **Camera** needs `localhost` or HTTPS; uploads always work.
* **Server:** Flask's built-in server is fine for demos; use a production WSGI server for real deployment.
* **Sample municipality figures** on the dashboard are illustrative and labelled "sample data".
* **PPT vs final build:** the proposal named Streamlit; the final app is Flask. Per-city rules, rule source URLs/review dates and training-time augmentation were out of scope for this app version.

## 8 · Team video

Add the presentation video link here before submission: **[Team presentation video](PASTE_VIDEO_LINK_HERE)**
