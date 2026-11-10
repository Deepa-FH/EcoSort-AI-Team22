"""FallbackResponder - answers from local rules when the LLM is unavailable."""

from __future__ import annotations

from .recycling_rule import RecyclingRule


class FallbackResponder:
    """Builds a useful answer from a rule alone (no network, no cost)."""

    NO_RULE_TEXT = ("I could not match that item to a local rule. "
                    "Please check your municipality's recycling guidance.")

    def respond(self, rule: RecyclingRule | None) -> str:
        """Text for ``rule``, or a safe 'unknown' message when ``rule`` is None."""
        if rule is None:
            return self.NO_RULE_TEXT
        return (f"Object: {rule.category}\nBin: {rule.bin} ({rule.bin_de})\n"
                f"Reason: {rule.note}\nConfidence: medium\n"
                "Note: Offline answer from the local rules - check local municipal rules "
                "and any deposit (Pfand) symbol.")
