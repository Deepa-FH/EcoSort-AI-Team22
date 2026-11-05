class DatasetStatistics:
    """Tracks class counts and imbalance; owned by Deepa Halapeti."""
    def __init__(self, class_counts: dict[str, int] | None = None) -> None:
        self._class_counts = class_counts or {}

    def initialize(self) -> None:
        self._class_counts = dict(self._class_counts)

    def get_class_counts(self) -> dict[str, int]:
        return dict(self._class_counts)

    def set_class_counts(self, counts: dict[str, int]) -> None:
        if any(value < 0 for value in counts.values()):
            raise ValueError("Class counts cannot be negative.")
        self._class_counts = dict(counts)

    def add_sample(self, label: str) -> None:
        self._class_counts[label] = self._class_counts.get(label, 0) + 1

    def total(self) -> int:
        return sum(self._class_counts.values())
