from typing import Any

# from app.routes.web.tabs.contacts import CONTACTS_TABS
# from app.routes.web.tabs.companies import COMPANIES_TABS
# from app.routes.web.tabs.opportunities import OPPORTUNITIES_TABS
# from app.routes.web.tabs.users import USERS_TABS
# from app.routes.web.tabs.tasks import TASKS_TABS
# from app.routes.web.tabs.settings import SETTINGS_TABS

# UI_TAB_MAPPING = {
#     "Contact": CONTACTS_TABS,
#     "Company": COMPANIES_TABS,
#     "Opportunity": OPPORTUNITIES_TABS,
#     "User": USERS_TABS,
#     "Task": TASKS_TABS,
#     "Setting": SETTINGS_TABS,
# }

PLURAL_MAP = {
    "Company": "companies",
    "Opportunity": "opportunities",
    "Category": "categories",
    "Capability": "capabilities",
}


def get_page_tabs(table_name):
    return UI_TAB_MAPPING[table_name]


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
