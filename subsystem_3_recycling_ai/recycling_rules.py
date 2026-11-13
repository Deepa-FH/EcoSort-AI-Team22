"""RecyclingRuleEngine - looks up and edits disposal rules."""

from __future__ import annotations

from .exceptions import InvalidRuleError, UnknownMaterialError
from .recycling_rule import RecyclingRule
from .rule_store import RuleStore


class RecyclingRuleEngine:
    """Rule-based guidance (the baseline of Subsystem 3; the LLM is optional).

    Rules are read from the injected ``RuleStore`` on every call, so an
    administrator's edit is visible immediately.
    """

    def __init__(self, store: RuleStore):
        self._store = store

    # ---- reading ---------------------------------------------------------
    def all(self) -> dict[str, RecyclingRule]:
        """Every rule, keyed by model label."""
        return {label: RecyclingRule.from_dict(data) for label, data in self._store.fetch_rules().items()}

    def get(self, label: str | None) -> RecyclingRule | None:
        """The rule for ``label`` or ``None`` (case-sensitive model label)."""
        return self.all().get(label) if label else None

    def require(self, label: str) -> RecyclingRule:
        """Like ``get`` but raises ``UnknownMaterialError`` when missing."""
        rule = self.get(label)
        if rule is None:
            raise UnknownMaterialError(f"No rule for label {label!r}")
        return rule

    def as_dicts(self) -> dict[str, dict]:
        """All rules as plain dicts (used by templates and JSON answers)."""
        return {label: rule.to_dict() for label, rule in self.all().items()}

    def rules_as_text(self) -> str:
        """Rules as bullet lines, inserted into the LLM prompt as ground truth."""
        return "\n".join(f"- {label}: {r.bin} ({r.bin_de}). {r.note}" for label, r in self.all().items())

    def find_label_in_text(self, text: str) -> str | None:
        """Find which rule an LLM answer talks about (label, bin or German bin name)."""
        lowered = text.lower()
        for label, rule in self.all().items():
            if label.lower() in lowered or rule.bin.lower() in lowered or rule.bin_de.lower() in lowered:
                return label
        return None

    # ---- writing ---------------------------------------------------------
    def update(self, label: str, fields: dict[str, str]) -> RecyclingRule:
        """Edit a rule (admin feature).

        Raises ``UnknownMaterialError`` for an unknown label and
        ``InvalidRuleError`` if a required field is empty.
        """
        current = self.require(label)
        cleaned = {key: str(fields.get(key, "")).strip() for key in RecyclingRule.EDITABLE}
        updated = RecyclingRule.from_dict({**current.to_dict(), **cleaned})
        updated.validate()
        self._store.save_rule(label, cleaned)
        return updated
