# AI-Powered Waste Sorting & Recycling Assistant

# Presentation Link [YouTube] : **[Presentation video](https://youtu.be/jG0oKkq1iSs?is=QIMbuncBO9aFFdVv)**

# EcoSort AI — Home Assignment 1

This submission translates the class diagrams from the Team 22 capstone presentation into executable Python OOP classes. Each member implements four UML classes, exceeding the requirement of at least three unique classes per student.

## Team overview

| Team member | Subsystem | UML classes |
|---|---|---|
| Deepa Halapeti | Dataset and Preprocessing | `DatasetManager`, `PreprocessingPipeline`, `DatasetMetadata`, `DatasetSplit` |
| Prasad Hule | AI Image Recognition | `ImageRecognitionService`, `ImagePreprocessor`, `WasteClassificationModel`, `PredictionResult` |
| Mayuresh Kumbhar | Recycling Rules and Ask AI | `RecyclingGuidanceService`, `RecyclingRule`, `AskAIService`, `GuidanceResponse` |
| Vijay Kathiresan | Web App, Dashboard and Integration | `WasteSortingWebApp`, `IntegrationController`, `DashboardService`, `WasteRepository` |

Every class has a constructor, initialization/setup behaviour, encapsulated attributes, getters and setters. Public class and operation names intentionally match the capstone UML so the architecture can be traced directly to the code.

## System flow

1. `DatasetManager` loads and validates image records.
2. `PreprocessingPipeline` resizes and normalizes them, and `DatasetSplit` creates data groups.
3. `ImageRecognitionService` prepares an image and obtains a `PredictionResult` from `WasteClassificationModel`.
4. `RecyclingGuidanceService` selects a `RecyclingRule` or uses `AskAIService`, returning `GuidanceResponse`.
5. `IntegrationController` combines both results, `WasteRepository` saves them, and `DashboardService` calculates statistics.
6. `WasteSortingWebApp` represents the user-facing entry point.

## Run

Python 3.10 or newer is recommended. No external package, model download, database or API key is required for this educational UML demonstration.

```bash
python main.py
```

The local model class uses deterministic demonstration inference so the professor can run the assignment on any laptop. The production Sortly AI project can inject its real YOLO model into the same architecture.

## Folder structure

```text
main.py
diagrams/                         Mermaid UML diagrams
subsystem_1_dataset_preprocessing/ Deepa's four classes
subsystem_2_image_recognition/     Prasad's four classes
subsystem_3_recycling_ai/          Mayuresh's four classes
subsystem_4_web_integration/       Vijay's four classes
```

## UML diagrams

- [Rendered UML diagrams](UML_DIAGRAMS.md)
- [Complete capstone UML](diagrams/complete_capstone_uml.mmd)
- [Dataset and preprocessing](diagrams/subsystem_1_uml.mmd)
- [AI image recognition](diagrams/subsystem_2_uml.mmd)
- [Recycling rules and Ask AI](diagrams/subsystem_3_uml.mmd)
- [Web app and integration](diagrams/subsystem_4_uml.mmd)

