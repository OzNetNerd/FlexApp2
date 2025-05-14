from app.models.pages.srs import SRS
from app.forms.srs import SRSForm
from app.services.srs import SRSService
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.views.base_view import DashboardView, FilteredView, StatisticsView, RecordsView
from app.routes.web.pages.srs.views import (
    SRSReviewView, SRSBatchActionView, SRSAddCardView, SRSCategoryView,
    SRSLearningStageView, SRSDifficultyView, SRSPerformanceView, SRSReviewStrategyView
)
from app.services.srs.constants import DEFAULT_EASE_FACTOR

# Create service
srs_service = SRSService()

# Configure views
dashboard_view = ViewConfig(
    view_class=DashboardView,
    kwargs={
        "template_path": "pages/srs/dashboard.html",
        "title": "SRS Dashboard"
    },
    endpoint="dashboard"
)

filtered_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/srs/filtered_cards.html",
        "title": "Filtered Cards"
    },
    url="/cards"
)

statistics_view = ViewConfig(
    view_class=StatisticsView,
    kwargs={
        "template_path": "pages/srs/stats.html",
        "title": "SRS Statistics"
    },
    url="/stats"
)

records_view = ViewConfig(
    view_class=RecordsView,
    kwargs={
        "model_class": SRS,
        "template_path": "pages/srs/records.html",
        "title": "SRS Records"
    },
    url="/records"
)

due_cards_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/srs/due.html",
        "title": "Cards Due Today"
    },
    url="/due"
)

add_card_view = ViewConfig(
    view_class=SRSAddCardView,
    kwargs={
        "template_path": "pages/srs/add_card.html",
        "title": "Add New Card"
    },
    url="/add"
)

review_item_view = ViewConfig(
    view_class=SRSReviewView,
    kwargs={
        "template_path": "pages/srs/review.html",
        "title": "Review Card"
    },
    url="/<int:item_id>/review"
)

batch_action_view = ViewConfig(
    view_class=SRSBatchActionView,
    kwargs={},
    url="/batch-action"
)

category_view = ViewConfig(
    view_class=SRSCategoryView,
    kwargs={
        "template_path": "pages/srs/category.html",
        "title": "Category Cards"
    },
    url="/category/<string:category_type>"
)

learning_stage_view = ViewConfig(
    view_class=SRSLearningStageView,
    kwargs={
        "template_path": "pages/srs/filtered_cards.html"
    },
    url="/learning-stage/<stage>"
)

difficulty_view = ViewConfig(
    view_class=SRSDifficultyView,
    kwargs={
        "template_path": "pages/srs/filtered_cards.html"
    },
    url="/difficulty/<difficulty>"
)

performance_view = ViewConfig(
    view_class=SRSPerformanceView,
    kwargs={
        "template_path": "pages/srs/filtered_cards.html"
    },
    url="/performance/<performance>"
)

review_strategy_view = ViewConfig(
    view_class=SRSReviewStrategyView,
    kwargs={},
    url="/strategy/<strategy>"
)

review_batch_view = ViewConfig(
    view_class=SRSReviewStrategyView,
    kwargs={},
    url="/review-batch"
)

create_category_view = ViewConfig(
    view_class=SRSAddCardView,
    kwargs={},
    url="/categories/create"
)

# Create blueprint with all views
srs_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=SRS,
        form_class=SRSForm,
        service=srs_service,
        url_prefix="/srs",
        views={
            "dashboard": dashboard_view,
            "filtered": filtered_view,
            "statistics": statistics_view,
            "records": records_view,
            "due_cards": due_cards_view,
            "add_card": add_card_view,
            "review_item": review_item_view,
            "batch_action": batch_action_view,
            "category_view": category_view,
            "learning_stage": learning_stage_view,
            "difficulty": difficulty_view,
            "performance": performance_view,
            "review_strategy": review_strategy_view,
            "review_batch": review_batch_view,
            "create_category": create_category_view
        }
    )
)

# Export context classes for use in other modules
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
    "SRSContext",
    "SRSCardListContext",
    "SRSDashboardContext",
    "SRSReviewContext",
    "SRSCategoryContext",
    "SRSFilteredCardsContext",
    "SRSFilteredContext",
    "SRSAddCardContext",
]