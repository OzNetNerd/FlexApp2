from app.models import Contact
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig


create_crud_blueprint(BlueprintConfig(model_class=Contact))
