# Home Task 2 presentation guide

## Deepa Halapeti - event stream and iteration

Show `events.py` and `video_stream.py`. Explain that `RecognitionEvent` carries each live prediction. `VideoEventStream.__iter__()` returns the stream and `__next__()` reads one frame, runs detection and raises `StopIteration` at the end.

## Prasad Hule - real-time recognition

Show `yolo_adapter.py`. Explain how the existing local `best_model.pt` is loaded, bounding-box coordinates and confidence are extracted, and visual tags are calculated from box metrics.

## Mayuresh Kumbhar - ABC, inheritance and polymorphism

Show `StreamProcessor(ABC)` and its abstract `process()` method. Then show that `ConfidenceFilter`, `MaterialCategoryMapper`, `ConveyorRouteAssigner` and `FrameAnnotator` inherit the same API and are called polymorphically.

## Vijay Kathiresan - composition and integration

Show `build_pipeline()` in `main.py`. Explain that overloaded `|` creates a `ProcessingPipeline`. Show the `processed_events()` generator and run the video. Point to the prediction, confidence, material and route overlays.

## Demo commands

```powershell
python create_demo_video.py
python main.py
```

Press `Q` or Escape to stop the video window.
