# app/routes/web/srs.py
from app.models.pages.srs import SRSItem
from app.routes.web.blueprint_factory import create_crud_blueprint
from app.services.srs_service import SRSService

# Create the service instance
srs_service = SRSService()

# Create the blueprint
# srs_items_bp = create_crud_blueprint(SRSItem, service=srs_service, url_prefix="/srs")
srs_items_bp = create_crud_blueprint(SRSItem, service=srs_service)
