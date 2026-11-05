from dataclasses import dataclass


@dataclass(frozen=True)
class RecyclingRule:
    material: str
    bin_name: str
    instruction: str
    preparation: str


class RecyclingRuleEngine:
    def __init__(self, rules: dict[str, RecyclingRule]):
        self.rules = {key.lower(): value for key, value in rules.items()}

    @classmethod
    def default_rules(cls) -> "RecyclingRuleEngine":
        values = [
            RecyclingRule("glass", "Glass container", "Use the local glass collection.", "Empty and rinse it; remove lids."),
            RecyclingRule("metal", "Metal recycling", "Use the local metal or packaging collection.", "Empty and rinse cans."),
            RecyclingRule("paper", "Paper recycling", "Place clean paper in the paper collection.", "Keep it dry and remove plastic film."),
            RecyclingRule("plastic", "Packaging recycling", "Use the local packaging/plastic collection.", "Empty, rinse, and compress when appropriate."),
            RecyclingRule("waste", "Residual waste", "Place contaminated non-recyclable material in residual waste.", "Do not mix batteries or chemicals with it."),
        ]
        return cls({rule.material: rule for rule in values})

    def get(self, material: str) -> RecyclingRule | None:
        return self.rules.get(material.lower().strip())
