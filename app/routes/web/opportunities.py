from app.models import Opportunity
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig


opportunities_bp = create_crud_blueprint(BlueprintConfig(model_class=Opportunity))
