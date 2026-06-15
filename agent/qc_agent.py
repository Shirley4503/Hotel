FORBIDDEN_KEYWORDS = [
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "pragma",
    "attach",
    "detach",
    "vacuum"
]


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Ensure generated SQL is read-only and safe.
    """
    if not sql or not sql.strip():
        return False, "Empty SQL."

    cleaned = sql.strip().lower()

    if not cleaned.startswith("select"):
        return False, "Only SELECT queries are allowed."

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in cleaned:
            return False, f"Forbidden SQL keyword detected: {keyword}"

    # Prevent multiple statements
    if ";" in cleaned[:-1]:
        return False, "Multiple SQL statements are not allowed."

    return True, "SQL passed safety check."
