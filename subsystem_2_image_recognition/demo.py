"""Live demo for Subsystem 2.   Run:  python -m subsystem_2_image_recognition.demo

Runs the REAL trained model on the sample images, prints every prediction and
then accuracy / precision / recall / F1 (labels come from the file names).
"""

from pathlib import Path

from PIL import Image

from subsystem_1_dataset_preprocessing import DatasetManager      # re-use Subsystem 1

from .detector import WasteDetector
from .exceptions import ModelNotFoundError, RecognitionErrorHandler
from .model_evaluator import ModelEvaluator
from .recognition_service import ImageRecognitionService

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    detector = WasteDetector(ROOT / "models" / "best_model.pt")
    service = ImageRecognitionService(detector)
    service.start()
    print("Model      :", detector.model_version)
    print("Classes    :", detector.labels, "\n")

    pairs = []
    for record in DatasetManager(ROOT / "sample_data").load_dataset():
        result = service.recognize(Image.open(record.path).convert("RGB"), threshold_percent=50)
        top = result.top
        predicted = top.label if top else None
        pairs.append((record.label, predicted))
        shown = f"{top.label} {top.confidence:.0%}" if top else "nothing found"
        flag = "OK " if predicted == record.label else "MISS"
        print(f"{flag} {record.filename:<48} -> {shown:<18} review={result.needs_review}")

    print("\n" + ModelEvaluator().evaluate(pairs).summary())
    print("\nError handler demo:", RecognitionErrorHandler().handle(ModelNotFoundError()).to_dict())


if __name__ == "__main__":
    main()
