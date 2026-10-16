from dataclasses import dataclass


@dataclass(frozen=True)
class QuerySpec:
    intent: str
    metric: str
    region: str | None


def understand(question: str) -> QuerySpec:
    lowered = question.lower()
    region = next((r for r in ("North", "South", "West") if r.lower() in lowered), None)
    intent = "policy_question" if any(term in lowered for term in ("policy", "campaign", "document")) and not any(
        term in lowered for term in ("revenue", "sales", "decline", "compare", "trend", "why")
    ) else "root_cause" if any(term in lowered for term in ("why", "decline", "cause", "driver")) else "comparison"
    return QuerySpec(intent, "revenue", region)
