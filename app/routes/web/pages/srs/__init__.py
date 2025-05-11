"""
SRS (Spaced Repetition System) package.

This package contains all the routes and context classes related to
the Spaced Repetition System functionality of the application.
"""
from flask import Flask
from app.services.srs_service import SRSService
from app.models.pages.srs import SRS
from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.utils.app_logging import get_logger

logger = get_logger()

# Define missing constant
DEFAULT_EASE_FACTOR = 2.5

# Create the service instance
logger.info("Initializing SRS service")
srs_service = SRSService()

# Create the blueprint config
logger.info("Creating SRS blueprint configuration")
srs_config = BlueprintConfig(model_class=SRS, service=srs_service)

# Create the blueprint using the config
logger.info("Creating SRS blueprint")
srs_bp = create_crud_blueprint(srs_config)

# Export context classes for use in route modules
from app.routes.web.pages.srs.contexts import (
    SRSContext,
    SRSCardListContext,
    SRSDashboardContext,
    SRSReviewContext,
    SRSCategoryContext,
    SRSFilteredCardsContext,
    SRSFilteredContext,
    SRSAddCardContext,
)

__all__ = [
    "srs_bp",
    "srs_service",
    "DEFAULT_EASE_FACTOR",
    "SRSContext",
    "SRSCardListContext",
    "SRSDashboardContext",
    "SRSReviewContext",
    "SRSCategoryContext",
    "SRSFilteredCardsContext",
    "SRSFilteredContext",
    "SRSAddCardContext",
]