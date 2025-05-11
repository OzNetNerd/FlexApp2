"""
SRS (Spaced Repetition System) package.

This package contains all the routes and context classes related to
the Spaced Repetition System functionality of the application.
"""
from app.routes.web.pages.srs.blueprint import srs_bp
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

# Route modules are automatically discovered by the auto-discovery system

__all__ = [
    "srs_bp",
    "SRSContext",
    "SRSCardListContext",
    "SRSDashboardContext",
    "SRSReviewContext",
    "SRSCategoryContext",
    "SRSFilteredCardsContext",
    "SRSFilteredContext",
    "SRSAddCardContext",
]