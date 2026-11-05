from .prompt_builder import PromptBuilder
from .rule_engine import RecyclingRuleEngine

class WasteAssistant:
    """Uses verified rules first and optional AI second; owned by Mayuresh Kumbhar."""
    def __init__(self, rule_engine: RecyclingRuleEngine, prompt_builder: PromptBuilder | None = None) -> None:
        self._rule_engine, self._prompt_builder = rule_engine, prompt_builder or PromptBuilder()
    def initialize(self) -> None: self._prompt_builder.initialize()
    def get_rule_engine(self) -> RecyclingRuleEngine: return self._rule_engine
    def set_rule_engine(self, value: RecyclingRuleEngine) -> None: self._rule_engine = value
    def get_guidance(self, category: str) -> dict[str, str]:
        rule = self._rule_engine.find_rule(category)
        if rule is None: return {"bin": "Check local authority guidance", "instruction": "No verified rule is available."}
        return {"bin": rule.get_bin_name(), "instruction": rule.get_instruction()}
