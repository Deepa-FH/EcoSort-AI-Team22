# EcoSort AI - architecture and UML overview

Detailed per-subsystem UML diagrams are in each subsystem's `README.md`. This page shows how they connect.

## Layers and dependencies

```mermaid
flowchart TB
  subgraph S4["Subsystem 4 - Web, Dashboard, Integration  (Vijay)"]
    APP[WasteSortingWebApp] --> CTRL[IntegrationController]
    CTRL --> SCAN[ScanService]
    CTRL --> JOBS[ReviewJobManager]
    CTRL --> DASH[DashboardService]
    SCAN --> REPO[(WasteRepository / SQLite)]
    APP --> AUTH[AuthService]
  end
  subgraph S1["Subsystem 1 - Dataset & Preprocessing  (Deepa)"]
    VAL[ImageValidator] --> PIPE[PreprocessingPipeline]
  end
  subgraph S2["Subsystem 2 - Image Recognition  (Prasad)"]
    REC[ImageRecognitionService] --> DET[WasteDetector] --> LOAD[ModelLoader]
    REC --> FILT[ConfidenceFilter]
  end
  subgraph S3["Subsystem 3 - Rules & Ask AI  (Mayuresh)"]
    ASSIST[WasteAssistant] --> ENG[RecyclingRuleEngine]
    ASSIST --> LLM[OpenAICompatibleClient]
    ASSIST --> PB[PromptBuilder]
  end
  SCAN --> VAL
  SCAN --> PIPE
  SCAN --> REC
  SCAN --> ENG
  JOBS --> ASSIST
  ENG -. RuleStore protocol .-> REPO
  ERR[shared: EcoSortError + BaseErrorHandler] -.-> S1
  ERR -.-> S2
  ERR -.-> S3
  ERR -.-> S4
```

## Error-handling hierarchy

```mermaid
classDiagram
EcoSortError <|-- PreprocessingError
EcoSortError <|-- RecognitionError
EcoSortError <|-- RecyclingAIError
EcoSortError <|-- WebDashboardError
PreprocessingError <|-- EmptyImageError
PreprocessingError <|-- UnsupportedImageError
PreprocessingError <|-- CorruptImageError
PreprocessingError <|-- ImageTooLargeError
PreprocessingError <|-- ImageTooSmallError
RecognitionError <|-- ModelNotFoundError
RecognitionError <|-- InvalidConfidenceError
RecognitionError <|-- InferenceError
RecyclingAIError <|-- LLMServiceError
LLMServiceError <|-- MissingAPIKeyError
RecyclingAIError <|-- UnknownMaterialError
RecyclingAIError <|-- InvalidRuleError
WebDashboardError <|-- AuthenticationError
WebDashboardError <|-- MissingUploadError
WebDashboardError <|-- ValidationFailedError
BaseErrorHandler <|-- DatasetErrorHandler
BaseErrorHandler <|-- RecognitionErrorHandler
BaseErrorHandler <|-- RecyclingAIErrorHandler
BaseErrorHandler <|-- WebDashboardErrorHandler
```

## Sequence: scanning an uncertain photo

```mermaid
sequenceDiagram
  participant B as Browser
  participant W as WasteSortingWebApp
  participant C as IntegrationController
  participant S as ScanService
  participant J as ReviewJobManager
  B->>W: POST /api/analyze (photo, threshold)
  W->>C: analyze_photo()
  C->>S: analyze()
  S->>S: validate + preprocess (S1), YOLO (S2), rule (S3), save scan (S4)
  S-->>C: result (needs_review = true)
  C->>J: start() background thread
  C-->>B: JSON (top label, route, job_id)
  J->>J: WasteAssistant.review_detection() (LLM or local fallback)
  loop every 1.4 s
    B->>W: GET /api/review/job_id
    W-->>B: working / done (answer, source)
  end
```

## Mapping to the original capstone UML

The proposal's diagrams named the first-draft classes; the working project grew them as follows.

| Proposal class (Home Task 1) | Class in the final code |
|---|---|
| `DatasetManager`, `DatasetMetadata`, `DatasetSplit`, `PreprocessingPipeline` | same names, now with real logic (+ `ImageValidator`, `ImageLoader`, `DatasetStatistics`) |
| `ImageRecognitionService`, `WasteClassificationModel`, `PredictionResult`, `ImagePreprocessor` | `ImageRecognitionService`, `WasteDetector` + `ModelLoader`, `PredictionResult`, (preprocessing moved to Subsystem 1's pipeline) |
| `RecyclingGuidanceService`, `RecyclingRule`, `AskAIService`, `GuidanceResponse` | `WasteAssistant`, `RecyclingRule` + `RecyclingRuleEngine`, `OpenAICompatibleClient` + `PromptBuilder`, `GuidanceResponse` |
| `WasteSortingWebApp`, `IntegrationController`, `DashboardService`, `WasteRepository` | same names |
