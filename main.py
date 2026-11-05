from dataclasses import dataclass

class ImageLoader: pass
class ImageValidator: pass
class PreprocessingPipeline: pass
class WasteDetector: pass
@dataclass
class Detection: label: str; confidence: float
@dataclass
class BoundingBox: x1: float; y1: float; x2: float; y2: float
class ConfidenceFilter: pass
@dataclass
class RecyclingRule: material: str; bin_name: str
class RecyclingRuleEngine: pass
class PromptBuilder: pass
class WasteAssistant: pass
class DashboardController: pass
class RequestValidator: pass
class ErrorHandler: pass

if __name__ == "__main__":
    print("Home Task 1 main: 15 project classes are defined across four subsystems.")
