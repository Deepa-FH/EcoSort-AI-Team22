"""Live demo for Subsystem 1.   Run:  python -m subsystem_1_dataset_preprocessing.demo

Shows (in order): load -> validate -> statistics -> split -> manifest -> pipeline
-> error handling. Needs no API key and no model.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from .dataset_manager import DatasetManager
from .exceptions import DatasetErrorHandler, EmptyImageError
from .preprocessing_pipeline import PreprocessingPipeline, ResizeStep, RGBStep

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def main() -> None:
    manager = DatasetManager(SAMPLE_DIR)
    print("1) Loading dataset ...", len(manager.load_dataset()), "images")
    print("2) Validation        :", manager.validate_dataset())
    print("3) Statistics\n" + manager.statistics().report())
    print("4) Split             :", manager.split_dataset(),
          "| leakage?", manager.dataset_split.has_leakage())
    with TemporaryDirectory() as tmp:
        manifest = manager.export_manifest(Path(tmp) / "manifest.csv")
        print("5) Manifest written  :", manifest.name, f"({manifest.stat().st_size} bytes)")

    # Operator overloading: the | operator chains steps into a pipeline.
    pipeline = RGBStep() | ResizeStep(320)
    print("6) Pipeline          :", pipeline)
    first = Image.open(manager.records[0].path)
    print("   before/after size :", first.size, "->", pipeline.apply(first).size)

    # Error handling: every subsystem returns a *safe* response.
    print("7) Error handler     :", DatasetErrorHandler().handle(EmptyImageError()).to_dict())


if __name__ == "__main__":
    main()
