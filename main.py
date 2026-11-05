"""Runnable Home Assignment 1 demonstration for EcoSort AI Team 22."""

from subsystem_1_dataset_preprocessing import ImageLoader, ImageValidator, PreprocessingPipeline
from subsystem_2_image_recognition import ConfidenceFilter, DetectionResult, WasteDetector
from subsystem_3_recycling_ai import RecyclingRule, RecyclingRuleEngine, WasteAssistant
from subsystem_4_web_integration import ApplicationCoordinator, DashboardService, PredictionController, RequestValidator


def main() -> None:
    """Run one lightweight end-to-end classification example."""
    loader = ImageLoader(allowed_extensions={".jpg", ".jpeg", ".png"})
    validator = ImageValidator(max_size_mb=8)
    pipeline = PreprocessingPipeline(target_size=(640, 640))

    detector = WasteDetector(model_name="YOLO26", confidence_filter=ConfidenceFilter(0.50))
    detector.initialize(lambda _: [DetectionResult("Plastic", 0.91, "demo-model-v1")])

    rules = RecyclingRuleEngine(city="Dortmund")
    rules.initialize([
        RecyclingRule("Plastic", "Yellow bin", "Empty the packaging before disposal."),
        RecyclingRule("Paper", "Blue bin", "Keep paper clean and dry."),
    ])
    assistant = WasteAssistant(rules)
    controller = PredictionController(loader, validator, pipeline, detector, assistant)
    coordinator = ApplicationCoordinator(RequestValidator(), controller, DashboardService())

    response = coordinator.handle_demo_request("sample_bottle.jpg", b"example image bytes")
    print("EcoSort AI - Home Assignment 1")
    print("--------------------------------")
    for key, value in response.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
