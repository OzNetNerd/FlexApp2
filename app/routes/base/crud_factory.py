import logging
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import BaseContext
from app.utils.table_helpers import PLURAL_MAP

logger = logging.getLogger(__name__)


def register_crud_routes(blueprint, entity_name, template_dir="pages/crud", table_template="pages/tables"):
    """
    Register standard CRUD routes on a blueprint.

    Args:
        blueprint: Flask Blueprint to register routes on
        entity_name: Name of the entity (used in titles and messages)
        template_dir: Directory containing create/view/edit templates
        table_template: Directory containing table templates
    """
    logger.info(f"Starting route registration with entity_name={entity_name}, template_dir={template_dir}, table_template={table_template}")

    entity_title = entity_name.capitalize()
    plural_name = PLURAL_MAP.get(entity_name, f"{entity_name}s")

    logger.info(f"Derived entity_title={entity_title}, plural_name={plural_name}")

    @blueprint.route("/")
    def index():
        logger.info(f"Executing 'index' route for '{plural_name}'")
        context = BaseContext(title=plural_name.capitalize(), read_only=True)
        logger.info(f"Index context: {context}")
        return render_safely(f"{table_template}/{plural_name}.html", context, f"Failed to load {plural_name}.")

    @blueprint.route("/create")
    def create():
        logger.info(f"Executing create route for {entity_name}")
        context = BaseContext(title=f"Create {entity_title}")
        logger.info(f"Create context: {context}")
        return render_safely(f"{template_dir}/create.html", context, f"Failed to load create {entity_name} form.")

    @blueprint.route("/<int:item_id>")
    def view(item_id):
        logger.info(f"Executing view route for {entity_name} with item_id={item_id}")
        context = BaseContext(title=f"View {entity_title}", item_id=item_id)
        logger.info(f"View context: {context}")
        return render_safely(f"{template_dir}/view.html", context, f"Failed to load {entity_name} details.")

    @blueprint.route("/<int:item_id>/edit")
    def edit(item_id):
        logger.info(f"Executing edit route for {entity_name} with item_id={item_id}")
        context = BaseContext(title=f"Edit {entity_title}", item_id=item_id)
        logger.info(f"Edit context: {context}")
        return render_safely(f"{template_dir}/edit.html", context, f"Failed to load edit {entity_name} form.")

    logger.info(f"Registered CRUD routes for {entity_name} with blueprint={blueprint}")
