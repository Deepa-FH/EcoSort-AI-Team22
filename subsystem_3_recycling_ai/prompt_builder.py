class PromptBuilder:
    """Builds safe LLM prompts; owned by Mayuresh Kumbhar."""
    def __init__(self, language: str = "English") -> None:
        self._language = language; self._system_message = "Give concise advice and do not invent official rules."
    def initialize(self, system_message: str | None = None) -> None:
        if system_message: self._system_message = system_message
    def get_language(self) -> str: return self._language
    def set_language(self, value: str) -> None:
        if not value.strip(): raise ValueError("Language cannot be empty.")
        self._language = value
    def get_system_message(self) -> str: return self._system_message
    def build(self, category: str, city: str, question: str) -> str:
        return f"{self._system_message}\nLanguage: {self._language}\nCity: {city}\nCategory: {category}\nQuestion: {question}"
