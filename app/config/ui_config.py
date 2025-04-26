# app/config/ui_config.py

# Tab configurations for entities
# Format: {entity_name: {endpoint: [tabs]}}
ENTITY_TABS = {
    "company": {
        "create": [
            {"tab_name": "About", "active": True},
        ],
        "view": [
            {"tab_name": "Notes", "active": True},
            {"tab_name": "About", "active": False},
            # {"tab_name": "System Info", "active": False},
        ],
        "edit": [
            {"tab_name": "About", "active": True},
        ],
    },
    # Add more entities as needed
}


def get_tabs_for_entity(entity_table_name, endpoint, entity=None, read_only=True):
    """
    Get the tabs configuration for an entity and endpoint.

    Args:
        entity_table_name (str): The name of the entity table (e.g., "company")
        endpoint (str): The endpoint (e.g., "create", "view", "edit")
        entity (object, optional): The entity object for conditional tabs
        read_only (bool): Whether the view is in read-only mode

    Returns:
        list: List of tab configurations
    """
    entity_name = entity_table_name.lower()

    # Get base tabs for this entity and endpoint
    if entity_name in ENTITY_TABS and endpoint in ENTITY_TABS[entity_name]:
        tabs = ENTITY_TABS[entity_name][endpoint].copy()
    else:
        tabs = []

    # Add conditional tabs based on entity data
    if entity and entity_name == "company":
        # Example: Add "Capabilities" tab if company has capabilities
        if hasattr(entity, "capabilities") and entity.capabilities:
            tabs.append({"tab_name": "Capabilities", "active": False})

    return tabs