import logging
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

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
    entity_title = entity_name.capitalize()

    @blueprint.route("/")
    def index():
        context = Context(title=f"{entity_title}s")
        return render_safely(f"{table_template}/{entity_name}s.html", context, f"Failed to load {entity_name}s.")

    @blueprint.route('/create')
    def create():
        context = Context(title=f"Create {entity_title}")
        return render_safely(f"{template_dir}/create.html", context, f"Failed to load create {entity_name} form.")

    @blueprint.route('/<int:item_id>')
    def view(item_id):
        context = Context(title=f"View {entity_title}", item_id=item_id)
        return render_safely(f"{template_dir}/view.html", context, f"Failed to load {entity_name} details.")

    @blueprint.route('/<int:item_id>/edit')
    def edit(item_id):
        context = Context(title=f"Edit {entity_title}", item_id=item_id)
        return render_safely(f"{template_dir}/edit.html", context, f"Failed to load edit {entity_name} form.")

    logger.debug(f"Registered CRUD routes for {entity_name}")