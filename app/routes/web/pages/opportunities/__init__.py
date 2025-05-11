from app.models import Opportunity
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main opportunities blueprint
opportunities_bp = create_crud_blueprint(BlueprintConfig(model_class=Opportunity))

# Import and register routes from submodules
from . import dashboard, filters, statistics, views

# No need to import views as it's now redundant