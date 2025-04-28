# app/routes/web/opportunities.py
from models.pages.opportunity import Opportunity
from app.routes.web.blueprint_factory import create_crud_blueprint

opportunities_bp = create_crud_blueprint(Opportunity)