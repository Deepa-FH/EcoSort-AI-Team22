"""Built-in German disposal rules for the seven classes the model predicts.

These are the SEED values. The web app copies them into the SQLite ``rules``
table on first start; afterwards administrators edit them in the browser
("Update rules without code rewrites" - PPT requirement).
"""

from .recycling_rule import RecyclingRule

DEFAULT_RULES: list[RecyclingRule] = [
    RecyclingRule(
        "Biomuell", "Organic waste", "Brown organic bin", "Biotonne", "Brown", "#8B5E3C", "organic", "leaf",
        "Food scraps and accepted garden waste belong here. Check local rules for cooked food and compostable liners."),
    RecyclingRule(
        "Glass", "Glass", "Deposit return or glass container", "Pfandautomat / Altglascontainer",
        "Green / white / brown", "#4F8A67", "glass", "bottle",
        "Return deposit bottles first. Put non-deposit container glass into the matching white, green or brown container."),
    RecyclingRule(
        "Metal", "Metal", "Yellow bin or recycling centre", "Gelbe Tonne / Wertstoffhof", "Yellow", "#F4C542",
        "metal", "can",
        "Metal packaging usually belongs in the yellow bin. Other metal objects normally go to a recycling centre."),
    RecyclingRule(
        "Papier", "Paper & cardboard", "Blue paper bin", "Papiertonne", "Blue", "#3178C6", "paper", "paper",
        "Use for clean paper and flattened cardboard. Heavily soiled or coated paper may need residual waste."),
    RecyclingRule(
        "Plastic", "Plastic", "Deposit return or yellow bin", "Pfandautomat / Gelbe Tonne", "Yellow", "#F4C542",
        "plastic", "bottle",
        "Return bottles carrying a deposit symbol. Empty plastic packaging without a deposit usually goes in the yellow bin."),
    RecyclingRule(
        "Sondermuell", "Special waste", "Special collection point", "Schadstoffmobil / Sammelstelle", "Red",
        "#D94B4B", "special", "battery",
        "Batteries, chemicals and hazardous items must go to a designated collection point, never a household bin."),
    RecyclingRule(
        "Textile_Trash", "Textiles", "Reuse or textile collection", "Altkleidercontainer / Spende", "Orange",
        "#D9822B", "textile", "shirt",
        "Donate clean, wearable textiles or use a textile collection point. Wet or contaminated textiles follow local rules."),
]
