from typing import Any

PLURAL_MAP = {
    "Company": "companies",
    "Opportunity": "opportunities",
    "Category": "categories",
    "Capability": "capabilities",
    "SRSItem": "srs",
}


def get_table_plural_name(table_name):
    return PLURAL_MAP.get(table_name, f"{table_name.lower()}s")


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

    Args:
        table_name (str): The name of the table.

    Returns:
        str: A string representing the table ID (e.g., 'user_table').
    """
    return f"{table_name}_table"
