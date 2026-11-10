"""GuidanceResponse - the answer object returned by the assistant."""

from __future__ import annotations

from dataclasses import asdict, dataclass

#: Where an answer came from. Shown in the UI so users can tell AI text from official rules
#: (PPT: "Distinguish AI text from official rules").
SOURCE_LLM = "llm"
SOURCE_LOCAL = "local-fallback"


@dataclass(frozen=True)
class GuidanceResponse:
    """One piece of guidance.

    Attributes:
        answer:           the text shown to the user.
        source:           ``"llm"`` (AI wrote it) or ``"local-fallback"`` (rule text).
        label:            matching rule label (e.g. ``"Papier"``) or ``None``.
        bin_recommendation: bin name from the matching rule ("" if none).
        estimated_tokens: rough LLM usage (0 for local answers).
        notice:           optional warning, e.g. why the AI was not used.
    """

    answer: str
    source: str = SOURCE_LOCAL
    label: str | None = None
    bin_recommendation: str = ""
    estimated_tokens: int = 0
    notice: str | None = None

    @property
    def used_llm(self) -> bool:
        return self.source == SOURCE_LLM

    def to_dict(self) -> dict:
        return asdict(self)
