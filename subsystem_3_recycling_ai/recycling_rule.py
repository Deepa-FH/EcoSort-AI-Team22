class RecyclingRule:
    """Represents reviewed disposal guidance; owned by Mayuresh Kumbhar."""
    def __init__(self, category: str, bin_name: str, instruction: str) -> None:
        self._category, self._bin_name, self._instruction = category, bin_name, instruction
    def initialize(self) -> None:
        if not all((self._category, self._bin_name, self._instruction)): raise ValueError("Complete rule required.")
    def get_category(self) -> str: return self._category
    def set_category(self, value: str) -> None: self._category = value.strip()
    def get_bin_name(self) -> str: return self._bin_name
    def set_bin_name(self, value: str) -> None: self._bin_name = value.strip()
    def get_instruction(self) -> str: return self._instruction
    def set_instruction(self, value: str) -> None: self._instruction = value.strip()
