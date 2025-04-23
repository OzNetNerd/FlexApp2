from typing import Any

# Only define each irregular plural once
IRREGULAR_PLURALS = {
    "company": "companies",
    "opportunity": "opportunities",
    "category": "categories",
    "capability": "capabilities",
    "srsitem": "srs"
}


def get_normalized_key(key):
    """Normalize a key for case-insensitive lookup."""
    return key.lower()


def get_table_plural_name(table_name):
    """
    Get the plural form of a table name.

    Handles both case variants automatically.
    """
    normalized = get_normalized_key(table_name)
    plural = IRREGULAR_PLURALS.get(normalized)

    if plural:
        # If original was capitalized, capitalize the result
        return plural.capitalize() if table_name[0].isupper() else plural

    # Regular pluralization with 's'
    return f"{table_name}s" if table_name[0].isupper() else f"{table_name.lower()}s"


def get_entity_base_route(table_name):
    """
    Generate a blueprint route name from a table name.

    Args:
        table_name (str): The name of the table.

    Returns:
        str: A string representing the blueprint route (e.g., 'users_bp').
    """
    plural = get_table_plural_name(table_name).lower()
    return f"{plural}_bp"


def get_table_id_by_model(model: Any) -> str:
    """
    Generate a table ID string from a SQLAlchemy model object.

    Args:
        model (Any): A SQLAlchemy model class or instance with a `__tablename__` attribute.

    Returns:
        str: A string representing the table ID (e.g., 'user_table').
    """
    return f"{model.__tablename__}_table"


def get_table_id_by_name(table_name: str) -> str:
    """
    Generate a table ID string from a table name.

    Returns:
        str: A string representing the table ID (e.g., 'user_table').
    """
    return f"{table_name}_table"