"""DatasetSplit - reproducible train / validation / test split without leakage."""

from __future__ import annotations

import random

from .dataset_record import DatasetRecord
from .exceptions import DatasetError


class DatasetSplit:
    """Splits records into three disjoint groups.

    * Reproducible: the same ``seed`` always gives the same split.
    * No leakage: every record lands in exactly ONE group (``has_leakage``
      double-checks this).
    """

    def __init__(self, train_ratio: float = 0.7, validation_ratio: float = 0.2, seed: int = 42):
        self.train_ratio = train_ratio
        self.validation_ratio = validation_ratio
        self._seed = int(seed)
        self._train: list[DatasetRecord] = []
        self._validation: list[DatasetRecord] = []
        self._test: list[DatasetRecord] = []

    # ---- validated ratios (properties) ----------------------------------
    @property
    def train_ratio(self) -> float:
        return self._train_ratio

    @train_ratio.setter
    def train_ratio(self, value: float) -> None:
        if not 0 < value < 1:
            raise DatasetError("train_ratio must be between 0 and 1")
        self._train_ratio = float(value)

    @property
    def validation_ratio(self) -> float:
        return self._validation_ratio

    @validation_ratio.setter
    def validation_ratio(self, value: float) -> None:
        if not 0 <= value < 1:
            raise DatasetError("validation_ratio must be between 0 and 1")
        self._validation_ratio = float(value)

    @property
    def seed(self) -> int:
        return self._seed

    # ---- main behaviour -------------------------------------------------
    def split(self, records: list[DatasetRecord]) -> dict[str, int]:
        """Shuffle (with the fixed seed) and cut the list into three parts.

        The ``split`` field of each record is updated so the manifest shows it.
        Returns the size of each group.
        """
        if self._train_ratio + self._validation_ratio >= 1:
            raise DatasetError("train + validation ratio must be below 1 (test needs data)")
        shuffled = list(records)
        random.Random(self._seed).shuffle(shuffled)   # local RNG: no global state touched
        end_train = int(len(shuffled) * self._train_ratio)
        end_val = end_train + int(len(shuffled) * self._validation_ratio)
        self._train, self._validation, self._test = (
            shuffled[:end_train], shuffled[end_train:end_val], shuffled[end_val:])
        for name, group in (("train", self._train), ("validation", self._validation), ("test", self._test)):
            for record in group:
                record.split = name
        return self.sizes()

    def sizes(self) -> dict[str, int]:
        """Number of records per group."""
        return {"train": len(self._train), "validation": len(self._validation), "test": len(self._test)}

    def has_leakage(self) -> bool:
        """True if one image appears in more than one group (should be False)."""
        seen: set[str] = set()
        for group in (self._train, self._validation, self._test):
            paths = {r.path for r in group}
            if seen & paths:
                return True
            seen |= paths
        return False

    # ---- getters (read-only copies) -------------------------------------
    @property
    def train(self) -> list[DatasetRecord]: return list(self._train)
    @property
    def validation(self) -> list[DatasetRecord]: return list(self._validation)
    @property
    def test(self) -> list[DatasetRecord]: return list(self._test)
