# Presentation guide - Group 22

Each member: **~3 minutes** = story (what + why) → classes & OOP ideas → live demo → one honest limitation. Open the member's own subsystem folder on screen while talking.

## Before you present (checklist)
1. `python testing.py` → all green (shows the whole system works).
2. Start the app: `python main.py --api-key KEY` and sign in (`admin` / `admin`). Have 2 photos ready: one clear item, one blurry/odd item (triggers the AI review).
3. Slider in **Settings** at its default (65 %). On the login form choose **Sign in as: Administrator** for the full demo; show a *Municipality worker* (dashboard only) and a *Normal user* (assistant only) to demonstrate roles.

## Opening (whoever starts, 30 s)
"EcoSort AI recognises a waste item from a photo, tells you the German bin, and explains it with an AI when the model is unsure. We split it into four subsystems; every subsystem is a Python package with its own classes, error handling, tests and live demo. The proposal planned Streamlit; the final version uses Flask for a more flexible, mobile-friendly interface."

---

## 1 · Deepa Halapeti - Dataset & Preprocessing
**Story:** "No image reaches the model unless it is safe and clean."
**Show:** `subsystem_1_dataset_preprocessing/` → `image_validator.py`, `preprocessing_pipeline.py`
**Say:**
* `ImageValidator` guards every upload: format JPEG/PNG/WebP, size, pixels, readable, phone rotation fixed. Limits are private attributes changed only via validated properties → **encapsulation**.
* `ImageStep` is an **abstract base class**; `RGBStep` and `ResizeStep` **inherit** and implement `apply()`. `PreprocessingPipeline` calls `step.apply()` on each → **polymorphism**. `RGBStep() | ResizeStep(320)` works through `__or__` → **operator overloading**.
* `DatasetManager` **composes** validator, loader, split and metadata → loads, finds corrupt/duplicate images, splits train/val/test **without leakage** (seeded), writes a CSV **manifest** with checksums.
**Demo:** `python -m subsystem_1_dataset_preprocessing.demo`
**Likely questions:** *Why a pipeline of steps?* Easy to add/replace steps without changing others. *How do you prevent leakage?* Each record is assigned to exactly one split and `has_leakage()` checks it. *Augmentation?* Done during model training outside this app (be honest).

## 2 · Prasad Hule - AI Image Recognition
**Story:** "Turn a photo into a label with an honest confidence."
**Show:** `detector.py`, `detection_models.py`, `confidence_filter.py`, `recognition_service.py`
**Say:**
* Trained **YOLO** model, 7 classes, runs on CPU or GPU (`pick_device`).
* `ModelLoader` loads/caches weights; `WasteDetector` gets it by **dependency injection** (tests use a fake loader). A `Lock` makes it thread-safe.
* `Detection`/`BoundingBox`/`PredictionResult` are **frozen dataclasses**; `needs_review` is a computed property: best confidence < slider → ask the AI.
* `ConfidenceFilter` uses a **generator**; `DetectionStream` implements the **iterator protocol**.
* `ImageRecognitionService` is the only class the web app knows → the model can be replaced without touching the web code.
* `ModelEvaluator` computes accuracy/precision/recall/F1.
**Demo:** `python -m subsystem_2_image_recognition.demo` (18/18 on samples - say these are examples, not a held-out test).
**Questions:** *Why show uncertainty?* To avoid over-claiming - low confidence goes to review. *What if the model file is missing?* `ModelNotFoundError` → safe message, no stack trace.

## 3 · Mayuresh Kumbhar - Recycling Rules & Ask AI
**Story:** "Rules first, AI second, never crash."
**Show:** `recycling_rules.py`, `ai_assistant.py`, `llm_client.py`
**Say:**
* `RecyclingRule` is a dataclass; `RecyclingRuleEngine` reads rules through a `RuleStore` **protocol** - in-memory for tests, SQLite in production → **polymorphism**. Admins edit rules in the browser; no code change.
* `PromptBuilder` creates prompts; `OpenAICompatibleClient` calls the API. **The API key comes only from `--api-key` or `LLM_API_KEY`** and `repr()` never prints it.
* `WasteAssistant` **composes** engine + client + prompts + fallback: tries the AI, and on any failure returns the local rule with a notice (`source = local-fallback`). The UI shows whether text came from AI or rules.
**Demo:** `python -m subsystem_3_recycling_ai.demo` (fallback), then with `--api-key KEY` (real answer).
**Questions:** *What if there is no internet?* Local fallback. *Why not only the AI?* Rules are the trusted baseline; AI explains (PPT: "keep paid LLM optional"). *Limitation:* one rule set for Dortmund; per-city rules are future work.

## 4 · Vijay Kathiresan - Web App, Dashboard & Integration
**Story:** "One app that connects everything - and is safe to use."
**Show:** `application_factory.py` (read top to bottom), `scan_service.py`, `waste_sorting_web_app.py`, the UI
**Say:**
* `create_application()` is the **composition root**: the only place where objects are created and wired → easy to test with fakes.
* `WasteSortingWebApp` is the Flask app **as a class**; routes only translate HTTP ↔ `IntegrationController` (a **facade**). `ScanService` runs the 6 steps across subsystems 1-3. `WasteRepository` holds all SQL (**repository pattern**) and also satisfies Subsystem 3's `RuleStore`.
* Security: hashed passwords, login required, admin-only rules, upload limit, safe error JSON from the four **error handlers** (inheritance from `BaseErrorHandler`).
* UI: responsive glassmorphism, light/dark, works on phone; dashboard with live charts, filters, CSV export.
**Demo:** upload clear photo → result + bin; upload odd photo → "asking AI" → answer; open Dashboard (filters), History (search), Rules (admin edit → effect immediately).
**Questions:** *Why Flask not Streamlit?* More control over layout/mobile and API structure. *Where is data stored?* SQLite (4 tables). *Docker?* `docker run -p 5000:5000 -e LLM_API_KEY=KEY ecosort-ai`. *Limitation:* sample municipality figures; default admin account is demo-only.

---

## Closing (30 s)
"Four subsystems, 30+ classes, a shared error hierarchy, 54 automated tests, one command to run with Python and one with Docker. Thank you - questions?"

## Quick demo script (copy/paste)
```bash
python testing.py                                   # 54 tests
python -m subsystem_1_dataset_preprocessing.demo
python -m subsystem_2_image_recognition.demo
python -m subsystem_3_recycling_ai.demo --api-key KEY
python main.py --api-key KEY                        # full app
docker run -p 5000:5000 -e LLM_API_KEY=KEY ecosort-ai
```
