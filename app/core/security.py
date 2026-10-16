import re

INJECTION_PATTERNS = (
    r"ignore (all |previous |prior )?instructions",
    r"system prompt",
    r"reveal (your |the )?(prompt|secret|credential)",
    r"<\s*/?(system|instruction)",
)


def screen_input(text: str) -> list[str]:
    """Return guardrail warnings; callers decide whether to reject the request."""
    return ["Potential prompt-injection language detected."] if any(
        re.search(pattern, text, re.IGNORECASE) for pattern in INJECTION_PATTERNS
    ) else []


def scrub_text(text: str) -> str:
    return re.sub(r"(?i)(api[_-]?key|password|secret)\s*[:=]\s*\S+", r"\1=[REDACTED]", text)
