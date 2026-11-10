"""ModelEvaluator - accuracy / precision / recall / F1 (PPT requirement #9)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvaluationReport:
    """Result of an evaluation run."""

    total: int
    correct: int
    per_class: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def accuracy(self) -> float:
        return round(self.correct / self.total, 4) if self.total else 0.0

    @property
    def macro_f1(self) -> float:
        """Average F1 over all classes (each class counts equally)."""
        scores = [c["f1"] for c in self.per_class.values()]
        return round(sum(scores) / len(scores), 4) if scores else 0.0

    def summary(self) -> str:
        lines = [f"Images: {self.total}  Correct: {self.correct}  Accuracy: {self.accuracy:.1%}  "
                 f"Macro-F1: {self.macro_f1:.3f}",
                 f"{'class':<14}{'precision':>10}{'recall':>8}{'f1':>7}{'n':>5}"]
        for label, m in sorted(self.per_class.items()):
            lines.append(f"{label:<14}{m['precision']:>10.2f}{m['recall']:>8.2f}{m['f1']:>7.2f}{int(m['support']):>5}")
        return "\n".join(lines)


class ModelEvaluator:
    """Computes classification metrics from (true label, predicted label) pairs.

    Pure Python - needs no numpy/sklearn - so it is easy to read and to test.
    """

    NO_DETECTION = "no_detection"

    def evaluate(self, pairs: list[tuple[str, str | None]]) -> EvaluationReport:
        """Build the report. ``None`` as prediction means "nothing detected"."""
        labels = sorted({true for true, _ in pairs})
        per_class: dict[str, dict[str, float]] = {}
        for label in labels:
            tp = sum(1 for t, p in pairs if t == label and p == label)
            fp = sum(1 for t, p in pairs if t != label and p == label)
            fn = sum(1 for t, p in pairs if t == label and p != label)
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}
        correct = sum(1 for t, p in pairs if t == p)
        return EvaluationReport(len(pairs), correct, per_class)
