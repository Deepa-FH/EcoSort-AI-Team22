class RequestValidator:
    """Validates web request fields; owned by Vijay Kathiresan."""
    def __init__(self, required_field: str = "image") -> None: self._required_field = required_field
    def initialize(self) -> None:
        if not self._required_field: raise ValueError("Required field cannot be empty.")
    def get_required_field(self) -> str: return self._required_field
    def set_required_field(self, value: str) -> None:
        if not value.strip(): raise ValueError("Required field cannot be empty.")
        self._required_field = value
    def validate(self, filename: str, content: bytes) -> bool:
        if not filename or not content: raise ValueError("An image filename and content are required.")
        return True
