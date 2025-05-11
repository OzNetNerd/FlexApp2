"""
SRS (Spaced Repetition System) package.

This package contains all the routes and context classes related to
the Spaced Repetition System functionality of the application.
"""
# Import from blueprint.py instead of duplicating
from app.routes.web.pages.srs.blueprint import srs_bp, srs_service, DEFAULT_EASE_FACTOR

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