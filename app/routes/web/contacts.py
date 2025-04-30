from app.models import Contact
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig


contacts_bp = create_crud_blueprint(BlueprintConfig(model_class=Contact))
