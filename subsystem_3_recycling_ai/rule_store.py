"""Where rules are stored.

OOP idea: POLYMORPHISM through a PROTOCOL (duck typing). The rule engine only
needs an object with ``fetch_rules()`` and ``save_rule()``. Two classes provide
them:
    * ``InMemoryRuleStore``  (this file)   - used by tests and the demo
    * ``WasteRepository``    (Subsystem 4) - stores rules in SQLite
The engine works with both and never knows which one it has.
"""

from __future__ import annotations

from typing import Protocol

from .default_rules import DEFAULT_RULES


class RuleStore(Protocol):
    """Anything that can load and save rules as ``{label: dict}``."""

    def fetch_rules(self) -> dict[str, dict]: ...

    def save_rule(self, label: str, fields: dict[str, str]) -> None: ...


class InMemoryRuleStore:
    """Keeps rules in a dict (lost when the program ends)."""

    def __init__(self):
        self._rules = {rule.label: rule.to_dict() for rule in DEFAULT_RULES}

    def fetch_rules(self) -> dict[str, dict]:
        return {label: dict(rule) for label, rule in self._rules.items()}

    def save_rule(self, label: str, fields: dict[str, str]) -> None:
        self._rules[label].update(fields)
