"""DatasetStatistics - class counts and imbalance report (PPT: "Report class
counts and imbalance")."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .dataset_record import DatasetRecord, parse_filename


@dataclass(frozen=True)
class DatasetStatistics:
    """Immutable summary of a dataset (``frozen=True`` => cannot be changed)."""

    total_images: int
    extensions: dict[str, int] = field(default_factory=dict)
    class_counts: dict[str, int] = field(default_factory=dict)

    # ---- alternative constructors (classmethods) ------------------------
    @classmethod
    def from_folder(cls, folder: Path | str) -> "DatasetStatistics":
        """Count files, extensions and classes in ``folder`` (recursive)."""
        files = [p for p in Path(folder).rglob("*") if p.is_file()]
        extensions = Counter(p.suffix.lower() or "[none]" for p in files)
        labels = Counter(parse_filename(p.name)[1] for p in files)
        return cls(len(files), dict(extensions), dict(labels))

    @classmethod
    def from_records(cls, records: Iterable[DatasetRecord]) -> "DatasetStatistics":
        """Build the summary from manifest records."""
        records = list(records)
        extensions = Counter(Path(r.filename).suffix.lower() or "[none]" for r in records)
        labels = Counter(r.label for r in records)
        return cls(len(records), dict(extensions), dict(labels))

    # ---- derived values -------------------------------------------------
    @property
    def imbalance_ratio(self) -> float:
        """Largest class size divided by smallest (1.0 = perfectly balanced)."""
        if not self.class_counts:
            return 1.0
        sizes = self.class_counts.values()
        return round(max(sizes) / max(1, min(sizes)), 2)

    def report(self) -> str:
        """Human-readable multi-line report (printed by the demo)."""
        lines = [f"Total images : {self.total_images}",
                 f"Extensions   : {self.extensions}",
                 f"Imbalance    : {self.imbalance_ratio}x (largest / smallest class)"]
        lines += [f"  {label:<14} {count}" for label, count in sorted(self.class_counts.items())]
        return "\n".join(lines)
