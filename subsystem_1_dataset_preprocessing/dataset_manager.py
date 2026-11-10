"""DatasetManager - the facade (front door) of Subsystem 1.

OOP idea: COMPOSITION. The manager does not do the work itself; it owns
a validator, a loader, a split object and a metadata object and coordinates
them. Replacing one of them (e.g. a stricter validator) needs no change here.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from .dataset_metadata import DatasetMetadata
from .dataset_record import DatasetRecord, parse_filename
from .dataset_split import DatasetSplit
from .dataset_statistics import DatasetStatistics
from .exceptions import DatasetError, PreprocessingError
from .image_loader import ImageLoader
from .image_validator import ImageValidator
from .preprocessing_pipeline import PreprocessingPipeline

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


class DatasetManager:
    """Scan, validate, split and document an image dataset."""

    def __init__(self, dataset_path: Path | str,
                 metadata: DatasetMetadata | None = None,
                 validator: ImageValidator | None = None,
                 split: DatasetSplit | None = None,
                 pipeline: PreprocessingPipeline | None = None):
        # Dependency injection: callers may pass their own collaborators (tests do).
        self._dataset_path = Path(dataset_path)
        self.metadata = metadata or DatasetMetadata()
        self.validator = validator or ImageValidator()
        self.dataset_split = split or DatasetSplit()
        self.pipeline = pipeline or PreprocessingPipeline.default()
        self.loader = ImageLoader()
        self._records: list[DatasetRecord] = []

    # ---- accessors -------------------------------------------------------
    @property
    def dataset_path(self) -> Path:
        return self._dataset_path

    @dataset_path.setter
    def dataset_path(self, value: Path | str) -> None:
        self._dataset_path = Path(value)
        self._records = []            # old records belong to the old folder

    @property
    def records(self) -> list[DatasetRecord]:
        return list(self._records)

    # ---- steps -----------------------------------------------------------
    def load_dataset(self) -> list[DatasetRecord]:
        """Find all supported images and create a record for each one.

        Raises ``DatasetError`` if the folder is missing or contains no images.
        """
        if not self._dataset_path.is_dir():
            raise DatasetError(f"Dataset folder not found: {self._dataset_path}")
        files = sorted(p for p in self._dataset_path.rglob("*") if p.suffix.lower() in SUPPORTED_SUFFIXES)
        if not files:
            raise DatasetError(f"No images found in {self._dataset_path}")
        self._records = []
        for path in files:
            source, label = parse_filename(path.name)
            self._records.append(DatasetRecord(path.name, str(path), label, source))
        return self.records

    def validate_dataset(self) -> dict[str, list[str]]:
        """Check every image; mark corrupt ones and detect duplicates.

        Returns ``{"corrupt": [...], "duplicates": [...]}`` (lists of filenames).
        """
        if not self._records:
            self.load_dataset()
        corrupt: list[str] = []
        duplicates: list[str] = []
        seen: dict[str, str] = {}
        for record in self._records:
            try:
                data = self.loader.load_bytes(record.path)
                self.validator.validate_and_prepare(data)       # raises if bad
                record.checksum = hashlib.sha256(data).hexdigest()
            except PreprocessingError:
                record.valid = False
                corrupt.append(record.filename)
                continue
            if record.checksum in seen:                         # same bytes seen before
                duplicates.append(record.filename)
            else:
                seen[record.checksum] = record.filename
        return {"corrupt": corrupt, "duplicates": duplicates}

    def split_dataset(self) -> dict[str, int]:
        """Assign train/validation/test to all VALID records."""
        valid = [r for r in self._records if r.valid]
        return self.dataset_split.split(valid)

    def statistics(self) -> DatasetStatistics:
        """Class counts and imbalance of the loaded records."""
        return DatasetStatistics.from_records(self._records)

    def export_manifest(self, csv_path: Path | str) -> Path:
        """Write the reproducible dataset manifest (CSV) and return its path.

        Columns: filename, path, label, source, checksum, split, valid.
        """
        csv_path = Path(csv_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(DatasetRecord("", "", "", "").to_dict()))
            writer.writeheader()
            for record in self._records:
                writer.writerow(record.to_dict())
        return csv_path

    def get_dataset_info(self) -> dict:
        """Short summary used by the demo and README."""
        return {"path": str(self._dataset_path), "images": len(self._records),
                **self.metadata.to_dict()}
