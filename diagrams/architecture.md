# System architecture

```text
Upload -> ImageValidator -> WasteDetector -> ConfidenceFilter -> Detection
                                                       |
                                                       v
                                          RecyclingRuleEngine -> PromptBuilder -> LLM API
                                                       |                         |
                                                       +---- local fallback <----+
```

The Flask dashboard is the integration boundary. The local model handles visual recognition; the remote API is used only for conversational wording.
