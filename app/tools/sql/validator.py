import re

from app.core.config import settings


class UnsafeQueryError(ValueError):
    pass


ALLOWED_RELATIONS = {"v_sales_enriched", "v_target_attainment"}
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|grant|revoke|attach|pragma|vacuum|replace|create)\b",
    re.IGNORECASE,
)


def validate_query(sql: str) -> str:
    normalized = " ".join(sql.strip().split())
    if not normalized:
        raise UnsafeQueryError("SQL is required.")
    if ";" in normalized or "--" in normalized or "/*" in normalized:
        raise UnsafeQueryError("Only one comment-free statement is allowed.")
    if not re.match(r"^(select|with)\b", normalized, re.IGNORECASE) or FORBIDDEN.search(normalized):
        raise UnsafeQueryError("Only SELECT or WITH ... SELECT statements are allowed.")
    relations = re.findall(r"\b(?:from|join)\s+([a-zA-Z_][\w]*)", normalized, re.IGNORECASE)
    if not relations or any(relation.lower() not in ALLOWED_RELATIONS for relation in relations):
        raise UnsafeQueryError("Query may access curated semantic views only.")
    if not re.search(r"\blimit\s+\d+\s*$", normalized, re.IGNORECASE):
        normalized = f"{normalized} LIMIT {settings.row_limit}"
    return normalized
