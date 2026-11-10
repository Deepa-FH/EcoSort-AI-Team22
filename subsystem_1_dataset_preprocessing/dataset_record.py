"""DatasetRecord - one row of the dataset manifest (one image)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


def parse_filename(name: str) -> tuple[str, str]:
    """Split ``<source>__<Label>__<original>.jpg`` into ``(source, label)``.

    Example: ``realwaste__Glass__Glass_360.jpg`` -> ``("realwaste", "Glass")``.
    Files that do not follow the convention return ``("unknown", "Unknown")``.
    """
    parts = Path(name).stem.split("__")
    if len(parts) >= 3:
        return parts[0], parts[1]
    return "unknown", "Unknown"


@dataclass
class DatasetRecord:
    """Metadata of one dataset image.

    A ``dataclass`` generates ``__init__``, ``__repr__`` and ``__eq__`` for us,
    which is perfect for plain data holders.
    """

    filename: str
    path: str
    label: str
    source: str
    checksum: str = ""      # SHA-256 of the file, used to find duplicates
    split: str = "unassigned"  # train / validation / test
    valid: bool = True      # False when the image is corrupt

    def to_dict(self) -> dict:
        """Return the record as a dict (used for the CSV manifest)."""
        return asdict(self)
