# app/routes/web/companies.py
from app.models.pages.company import Company
from app.routes.web.blueprint_factory import create_crud_blueprint

companies_bp = create_crud_blueprint(Company)
