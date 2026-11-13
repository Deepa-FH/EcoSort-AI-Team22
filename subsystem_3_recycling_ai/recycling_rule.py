"""RecyclingRule - one disposal rule (what to do with one waste class)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields

from .exceptions import InvalidRuleError


@dataclass
class RecyclingRule:
    """Disposal guidance for one model label.

    Attributes mirror the ``rules`` database table. ``label`` is the class name
    the YOLO model predicts (e.g. ``"Papier"``).
    """

    label: str          # model class name, e.g. "Papier"
    category: str       # friendly name, e.g. "Paper & cardboard"
    bin: str            # English bin name
    bin_de: str         # German bin name
    color: str          # colour of the bin (text)
    hex: str            # colour of the bin (for the UI), e.g. "#3178C6"
    theme: str          # UI theme key
    symbol: str         # UI icon key
    note: str           # preparation / explanation text

    #: Fields an administrator may edit in the web UI.
    EDITABLE = ("category", "bin", "bin_de", "color", "hex", "theme", "symbol", "note")

    def validate(self) -> None:
        """Raise ``InvalidRuleError`` if any field is empty."""
        missing = [f.name for f in fields(self) if not str(getattr(self, f.name)).strip()]
        if missing:
            raise InvalidRuleError(f"Rule {self.label!r} has empty fields: {missing}")

    def to_dict(self) -> dict:
        """Plain dict (JSON / database friendly)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RecyclingRule":
        """Create a rule from a dict; unknown keys (e.g. ``updated_at``) are ignored."""
        known = {f.name for f in fields(cls)}
        return cls(**{k: str(v) for k, v in data.items() if k in known})
