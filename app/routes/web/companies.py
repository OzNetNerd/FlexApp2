# app/routes/web/companies.py
from app.models.pages.company import Company
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig

# Simple usage with just the model class
config = BlueprintConfig(model_class=Company)
companies_bp = create_crud_blueprint(config)

# More customized example (commented out)
# config = BlueprintConfig(
#     model_class=Company,
#     url_prefix="/companies",
#     index_template="pages/companies/custom_index.html"
# )
# companies_bp = create_crud_blueprint(config)