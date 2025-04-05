from typing import Any


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
