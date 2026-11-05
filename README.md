# Home Task 2 - Real-Time Data Processing

## AI-Powered Waste Sorting & Recycling Assistant

Team 22 implements an event-driven stream pipeline for an automated conveyor-belt optical sorter. A local YOLO model reads video frames, uncertain predictions are filtered, bounding-box metrics and visual tags are transformed into material categories, and each accepted item receives a conveyor routing code.

## Team

| Team member | Matriculation no. | Presentation responsibility |
|---|---:|---|
| Deepa Halapeti | 7225894 | Events, `VideoEventStream`, iterators and `__next__` |
| Prasad Hule | 7225861 | Local YOLO adapter, bounding boxes and live predictions |
| Mayuresh Kumbhar | 7226310 | ABC, inheritance, polymorphism and stream processors |
| Vijay Kathiresan | 7226794 | Operator overloading, pipeline composition, generator and integration |

## Pipeline

```text
Video -> YOLO RecognitionEvent -> ConfidenceFilter -> MaterialCategoryMapper
      -> ConveyorRouteAssigner -> FrameAnnotator -> screen/output video
```

## Required OOP concepts

- **ABC:** `StreamProcessor(ABC)` defines the abstract `process()` contract.
- **Inheritance and polymorphism:** four specialized processors inherit the same interface and are executed uniformly.
- **Operator overloading:** `processor_a | processor_b` calls `__or__()` and builds a `ProcessingPipeline`.
- **Iterator:** `VideoEventStream` implements `__iter__()` and `__next__()`.
- **Generator:** `processed_events()` lazily yields each processed event.

## Main classes

| Class | Responsibility |
|---|---|
| `RecognitionEvent`, `BoundingBox` | Carry frame, prediction, confidence and geometry data |
| `YOLOModelAdapter` | Load `best_model.pt` and convert YOLO output |
| `VideoEventStream` | Consume one video frame at a time |
| `ConfidenceFilter` | Redirect low-confidence events to manual review |
| `MaterialCategoryMapper` | Map labels and visual tags to material categories |
| `ConveyorRouteAssigner` | Add an automated sorting route code |
| `FrameAnnotator` | Draw the live result on the frame |
| `ProcessingPipeline` | Compose and execute processors |

PET, HDPE and Aluminum are marked as **candidates** because the current model predicts broad classes such as Plastic and Metal. The mapping processor combines those labels with bounding-box visual tags; it does not claim laboratory-grade polymer identification.

## Folder structure

```text
├── main.py
├── create_demo_video.py
├── models/best_model.pt
├── media/conveyor_demo.mp4
├── media/video_manifest.json
├── realtime_pipeline/
│   ├── events.py, stream_processor.py, pipeline.py
│   ├── video_stream.py, yolo_adapter.py
│   └── processors/
├── output/                         # generated annotated video
└── PRESENTATION_GUIDE.md
```

## Installation

Python 3.11 or 3.12 is recommended. Open a terminal in the project folder and create a virtual environment.

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

Generate the 10.5-second input video from the 21 supplied images:

```powershell
python create_demo_video.py --images "PATH_TO_WASTE_IMAGES"
```

The repository already contains `media/conveyor_demo.mp4`, so this step is optional. Use it only to rebuild the demonstration video from another image folder.

Run real-time recognition, display the result, and save an annotated video:

```powershell
python main.py
```

Headless mode for a laptop or automated check:

```powershell
python main.py --no-display --frame-skip 1
```

Useful options:

```text
--video PATH        input MP4
--model PATH        local YOLO weights
--confidence 0.50   acceptance threshold
--frame-skip N      skip N frames between events
--no-display        do not open an OpenCV window
--no-save-output    do not save the annotated MP4
```

Press `Q` or Escape to close the display. See `PRESENTATION_GUIDE.md` for each member's explanation.

## Portability notes

- All normal runtime paths are relative to this project folder.
- The included model is loaded from `models/best_model.pt`.
- The default input is `media/conveyor_demo.mp4`.
- The annotated result is written to `output/conveyor_detected_output.mp4`.
- No API key, username, or device-specific path is required.
- If Torch is blocked or unsupported by the installed Python version, use Python 3.11 or 3.12 in a fresh virtual environment.
