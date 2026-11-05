from .recycling_rules import RecyclingRule


class PromptBuilder:
    def build(self, user_message: str, rule: RecyclingRule | None) -> str:
        context = "No local rule matched." if rule is None else f"Material: {rule.material}; bin: {rule.bin_name}; rule: {rule.instruction}; preparation: {rule.preparation}"
        return f"You are a concise recycling assistant. Use this local rule as the source of truth: {context}\nUser question: {user_message}\nAnswer clearly in 3 short sentences or fewer."
