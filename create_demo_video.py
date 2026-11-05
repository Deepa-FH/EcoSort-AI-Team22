"""Build a short conveyor-belt MP4 from the supplied waste images."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent


def expected_label(filename: str) -> str:
    parts = filename.split("__")
    return parts[1] if len(parts) > 2 else "Unknown"


def build_video(images_dir: Path, output: Path, seconds_per_item: float, fps: int) -> list[dict]:
    files = sorted(path for path in images_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not files:
        raise FileNotFoundError(f"No images found in {images_dir}")
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1280, 720
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create video: {output}")
    frames_per_item = max(1, round(seconds_per_item * fps))
    manifest = []
    for item_index, image_path in enumerate(files, start=1):
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        scale = min(580 / image.shape[1], 430 / image.shape[0])
        resized = cv2.resize(image, (int(image.shape[1] * scale), int(image.shape[0] * scale)))
        expected = expected_label(image_path.name)
        manifest.append({"item": item_index, "filename": image_path.name, "expected_broad_label": expected, "start_second": round((item_index - 1) * seconds_per_item, 2)})
        for local_frame in range(frames_per_item):
            canvas = np.full((height, width, 3), (231, 239, 234), dtype=np.uint8)
            cv2.rectangle(canvas, (0, 535), (width, 675), (59, 72, 66), -1)
            belt_offset = (local_frame * 30) % 120
            for x in range(-120 + belt_offset, width, 120):
                cv2.line(canvas, (x, 545), (x + 80, 665), (115, 130, 122), 6)
            progress = local_frame / max(1, frames_per_item - 1)
            center_x = int(width * (0.46 + 0.08 * progress))
            x1 = center_x - resized.shape[1] // 2
            y1 = 90 + (430 - resized.shape[0]) // 2
            canvas[y1:y1 + resized.shape[0], x1:x1 + resized.shape[1]] = resized
            cv2.putText(canvas, "EcoSort AI - Optical Sorter Input", (35, 48), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (24, 97, 64), 2, cv2.LINE_AA)
            cv2.putText(canvas, f"Conveyor item {item_index}/{len(files)}", (35, 705), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (25, 35, 30), 2, cv2.LINE_AA)
            writer.write(canvas)
    writer.release()
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True, help="Folder containing JPG or PNG waste images")
    parser.add_argument("--output", type=Path, default=ROOT / "media" / "conveyor_demo.mp4")
    parser.add_argument("--seconds", type=float, default=0.5, help="Seconds shown per item")
    parser.add_argument("--fps", type=int, default=20)
    args = parser.parse_args()
    manifest = build_video(args.images, args.output, args.seconds, args.fps)
    manifest_path = args.output.with_name("video_manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created {args.output} with {len(manifest)} items")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
