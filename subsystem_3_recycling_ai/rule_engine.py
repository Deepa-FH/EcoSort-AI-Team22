from .recycling_rule import RecyclingRule

class RecyclingRuleEngine:
    """Looks up city-specific guidance; owned by Mayuresh Kumbhar."""
    def __init__(self, city: str = "Dortmund") -> None: self._city, self._rules = city, {}
    def initialize(self, rules: list[RecyclingRule]) -> None: self._rules = {r.get_category().lower(): r for r in rules}
    def get_city(self) -> str: return self._city
    def set_city(self, value: str) -> None:
        if not value.strip(): raise ValueError("City cannot be empty.")
        self._city = value
    def get_rules(self) -> dict[str, RecyclingRule]: return dict(self._rules)
    def find_rule(self, category: str) -> RecyclingRule | None: return self._rules.get(category.lower())
