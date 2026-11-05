# EcoSort AI Team 22 Capstone Project

This branch contains the complete Waste Sorting and Recycling Assistant. It combines local YOLO image recognition, dataset and image preprocessing, recycling rules, an OpenAI-compatible Ask AI client, and a Flask dashboard.

## Run

```powershell
python -m pip install -r requirements.txt
$env:LLM_API_KEY="your-api-key"
python main.py --model models/best_model.pt
```

Place the trained checkpoint at `models/best_model.pt` or pass `--model PATH`. The LLM model and base URL are configurable. See `diagrams/` and `waste_sorting_project_presentation_guide.pdf` for the architecture, UML, team responsibilities, and presentation plan.
