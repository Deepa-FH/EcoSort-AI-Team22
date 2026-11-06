"""Run the EcoSort AI real-time conveyor stream pipeline."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

from realtime_pipeline import VideoEventStream, YOLOModelAdapter, processed_events
from realtime_pipeline.processors import ConfidenceFilter, ConveyorRouteAssigner, FrameAnnotator, MaterialCategoryMapper

ROOT = Path(__file__).resolve().parent


def build_pipeline(confidence: float):
    """The | operators call StreamProcessor.__or__ to compose the pipeline."""
    return ConfidenceFilter(confidence) | MaterialCategoryMapper() | ConveyorRouteAssigner() | FrameAnnotator()


def run(args: argparse.Namespace) -> dict[str, int | float]:
    detector = YOLOModelAdapter(args.model, confidence=min(args.confidence, 0.20))
    stream = VideoEventStream(args.video, detector, frame_skip=args.frame_skip)
    pipeline = build_pipeline(args.confidence)
    writer = None
    totals = {"frames": 0, "accepted": 0, "review": 0}
    started = time.perf_counter()
    try:
        iterator = iter(stream)  # explicitly exercises __iter__
        if args.save_output:
            width, height = stream.frame_size
            args.output.parent.mkdir(parents=True, exist_ok=True)
            output_fps = max(1.0, stream.fps / (args.frame_skip + 1))
            writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*"mp4v"), output_fps, (width, height))
        for event in processed_events(iterator, pipeline):  # generator consumes __next__
            totals["frames"] += 1
            totals["accepted" if event.accepted else "review"] += 1
            if writer is not None:
                writer.write(event.frame)
            if args.display:
                cv2.imshow("EcoSort AI - Real-Time Conveyor Detection", event.frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
            if totals["frames"] % 10 == 0:
                print(f"frame={event.frame_number:4d} label={event.model_label:14s} confidence={event.confidence:.1%} material={event.material_category:20s} route={event.routing_code}")
    finally:
        stream.close()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()
    elapsed = max(0.001, time.perf_counter() - started)
    totals["processing_fps"] = round(totals["frames"] / elapsed, 2)
    return totals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, default=ROOT / "media" / "conveyor_demo.mp4")
    parser.add_argument("--model", type=Path, default=ROOT / "models" / "best_model.pt")
    parser.add_argument("--confidence", type=float, default=0.50)
    parser.add_argument("--frame-skip", type=int, default=0)
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "conveyor_detected_output.mp4")
    parser.add_argument("--display", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-output", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


if __name__ == "__main__":
    options = parse_args()
    if not 0 <= options.confidence <= 1:
        raise SystemExit("--confidence must be between 0 and 1")
    summary = run(options)
    print("Completed:", summary)
    if options.save_output:
        print("Annotated video:", options.output)
