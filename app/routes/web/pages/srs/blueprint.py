"""
SRS blueprint configuration module.

This module initializes the SRS service and creates the blueprint
for SRS-related routes in the web application.
"""

from app.services.srs import SRSService
from app.models.pages.srs import SRS
from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.utils.app_logging import get_logger

logger = get_logger()

# Create the service instance
logger.info("Initializing SRS service")
srs_service = SRSService()

# Create the blueprint config
logger.info("Creating SRS blueprint configuration")
srs_config = BlueprintConfig(model_class=SRS, service=srs_service)

# Create the blueprint using the config
logger.info("Creating SRS blueprint")
srs_bp = create_crud_blueprint(srs_config)
