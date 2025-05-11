from app.models import Opportunity
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main opportunities blueprint
opportunities_bp = create_crud_blueprint(BlueprintConfig(model_class=Opportunity))