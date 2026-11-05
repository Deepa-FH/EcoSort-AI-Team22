from .recycling_rules import RecyclingRule


def fallback_response(rule: RecyclingRule | None) -> str:
    if rule is None:
        return "I could not match that material to a local rule. Check your municipality's recycling guidance."
    return f"Put it in {rule.bin_name}. {rule.instruction} {rule.preparation}"
