# EcoSort AI - Home Task 4

## Exception Handling and Unit Tests

This assignment adds subsystem-specific exceptions, safe error handlers, and exactly **15 automated tests** to the four subsystems of the Sortly AI capstone. Tests use small in-memory images and fake model/LLM objects, so they run without YOLO weights, a GPU, an API key, MySQL, or internet access.

## Team and subsystem ownership

| Team member | Matriculation no. | Subsystem | Error handler |
|---|---:|---|---|
| Deepa Halapeti | 7225894 | Dataset and Preprocessing | `DatasetErrorHandler` |
| Prasad Hule | 7225861 | AI Image Recognition | `RecognitionErrorHandler` |
| Mayuresh Kumbhar | 7226310 | Recycling Rules and Ask AI | `RecyclingAIErrorHandler` |
| Vijay Kathiresan | 7226794 | Web App, Dashboard and Integration | `WebDashboardErrorHandler` |

Each subsystem has a base exception, specialized exception subclasses, and a handler that returns an error code, safe message, HTTP status, and recoverability flag. Low-level failures use exception chaining (`raise ... from error`) while public responses hide internal paths, network details, and tracebacks.

## The 15 tests

| # | Subsystem | Scenario |
|---:|---|---|
| 1 | Dataset | Valid PNG is accepted and converted to RGB |
| 2 | Dataset | Empty upload raises `EmptyImageError` |
| 3 | Dataset | Unsupported and corrupt content raise specific errors |
| 4 | Dataset | Oversized upload raises `ImageTooLargeError` |
| 5 | Recognition | Valid confidence threshold is accepted |
| 6 | Recognition | Invalid threshold raises `InvalidConfidenceError` |
| 7 | Recognition | Missing weights raise `ModelNotFoundError` |
| 8 | Recognition | Predictor failure is chained as `InferenceError` |
| 9 | Recycling AI | Missing API key raises `MissingAPIKeyError` |
| 10 | Recycling AI | Network failure is chained as `LLMServiceError` |
| 11 | Recycling AI | Local rules are returned when the LLM fails |
| 12 | Web | Health endpoint returns HTTP 200 JSON |
| 13 | Web | Missing upload returns safe HTTP 400 JSON |
| 14 | Web | Corrupt upload returns safe HTTP 400 JSON |
| 15 | Web | Unexpected detector failure returns safe HTTP 500 JSON |

## Structure

```text
├── main.py
├── requirements.txt
├── pytest.ini
├── ecosort_testing/
│   ├── common.py
│   ├── dataset_errors.py
│   ├── recognition_errors.py
│   ├── recycling_ai_errors.py
│   ├── web_errors.py
│   ├── sample_services.py
│   └── flask_app.py
└── tests/
    ├── conftest.py
    ├── test_dataset_preprocessing.py
    ├── test_image_recognition.py
    ├── test_recycling_ai.py
    └── test_web_dashboard.py
```

`conftest.py` supplies reusable Pillow image, Flask application, and test-client fixtures. Flask's test client calls routes without starting a live server. Dependency injection supplies fake detectors and LLM clients, making failures deterministic and fast.

## Install and run

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run all tests:

```bash
python -m pytest -v
```

Expected result:

```text
15 passed
```

Run one subsystem:

```bash
python -m pytest tests/test_dataset_preprocessing.py -v
python -m pytest tests/test_image_recognition.py -v
python -m pytest tests/test_recycling_ai.py -v
python -m pytest tests/test_web_dashboard.py -v
```

Run the error-handler demonstration:

```bash
python main.py
```

## Capstone relationship

The test boundaries mirror the real capstone modules: `dataset_preprocessing`, `image_recognition`, `recycling_ai`, and the Flask web/dashboard integration. Heavy external dependencies are replaced only inside tests; the business rules and error behavior remain representative of Sortly AI.

## GitHub submission

Upload this folder to the Home Task 4 branch and add the branch URL here before submission:

```text
GitHub link: TO BE ADDED
```
