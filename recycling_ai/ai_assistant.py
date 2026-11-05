from .fallback_responses import fallback_response
from .llm_client import OpenAICompatibleClient
from .prompt_builder import PromptBuilder
from .recycling_rules import RecyclingRuleEngine


class WasteAssistant:
    def __init__(self, rules: RecyclingRuleEngine, llm: OpenAICompatibleClient, prompt_builder: PromptBuilder | None = None):
        self.rules = rules
        self.llm = llm
        self.prompt_builder = prompt_builder or PromptBuilder()

    def answer(self, material: str, message: str) -> dict[str, str | bool]:
        rule = self.rules.get(material)
        prompt = self.prompt_builder.build(message, rule)
        try:
            return {"answer": self.llm.ask(prompt), "source": "llm", "material": material}
        except Exception as error:
            print(f"[Ask AI] API unavailable, using local fallback: {error}")
            return {"answer": fallback_response(rule), "source": "local-fallback", "material": material}
