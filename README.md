# EcoSort AI — Home Assignment 1

This assignment translates the Team 22 capstone UML architecture into working Python OOP classes. It is a lightweight extension of the running **Sortly AI** Flask project: the same four subsystems are represented, but the demo does not require YOLO, Flask, a GPU, or an API key.

## Team and subsystem allocation

| Team member | Matriculation no. | Subsystem | Main classes |
|---|---:|---|---|
| Deepa Halapeti | 7225894 | Dataset and Preprocessing | `ImageLoader`, `ImageValidator`, `ImagePreprocessor`, `PreprocessingPipeline`, `DatasetStatistics` |
| Prasad Hule | 7225861 | AI Image Recognition | `ModelLoader`, `BoundingBox`, `DetectionResult`, `ConfidenceFilter`, `WasteDetector` |
| Mayuresh Kumbhar | 7226310 | Recycling Rules and Ask AI | `RecyclingRule`, `RecyclingRuleEngine`, `PromptBuilder`, `OpenAICompatibleClient`, `WasteAssistant` |
| Vijay Kathiresan | 7226794 | Web App, Dashboard and Integration | `RequestValidator`, `PredictionController`, `DashboardService`, `ApplicationCoordinator` |

Every member implements at least three unique classes. The classes contain constructors, initialized state, configuration methods, encapsulated attributes, getters and validated setters.

## System flow

`Upload → validation/preprocessing → image recognition → recycling rule/AI explanation → web response/dashboard`

The proposal mentioned Streamlit, while the final Sortly AI implementation evolved to Flask. These classes follow the responsibilities of the final Flask application.

## Folder structure

```text
├── main.py                         # Integrated demonstration
├── subsystem_1_dataset_preprocessing/
├── subsystem_2_image_recognition/
├── subsystem_3_recycling_ai/
├── subsystem_4_web_integration/
├── diagrams/                       # Complete and subsystem UML diagrams
└── TEAM_PRESENTATION_GUIDE.md      # 3–5 minute speaking plan
```

## Run

From this directory:

```powershell
python main.py
```

The demo uses sample bytes and a fake model result so it runs on any laptop. The production capstone separately loads the real YOLO model and receives the LLM key at runtime; no secret is stored here.

## UML diagrams

- [Complete system UML](diagrams/complete_capstone_uml.mmd)
- [Dataset and preprocessing](diagrams/subsystem_1_uml.mmd)
- [AI image recognition](diagrams/subsystem_2_uml.mmd)
- [Recycling rules and Ask AI](diagrams/subsystem_3_uml.mmd)
- [Web app and integration](diagrams/subsystem_4_uml.mmd)

## Presentation

Video link: **TO BE ADDED AFTER RECORDING**

Use [TEAM_PRESENTATION_GUIDE.md](TEAM_PRESENTATION_GUIDE.md) for the unified team explanation.
