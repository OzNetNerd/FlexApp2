from app.models.pages.opportunity import Opportunity
from app.forms.opportunity import OpportunityForm
from app.services.opportunity import OpportunityService
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.views.base_view import DashboardView, FilteredView, StatisticsView, RecordsView

# Create service
opportunity_service = OpportunityService()

# Configure views
dashboard_view = ViewConfig(
    view_class=DashboardView,
    kwargs={
        "template_path": "pages/opportunities/dashboard.html",
        "title": "Opportunities Dashboard"
    },
    endpoint="dashboard"
)

filtered_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/opportunities/filtered.html",
        "title": "Filtered Opportunities"
    },
    url="/filtered"
)

statistics_view = ViewConfig(
    view_class=StatisticsView,
    kwargs={
        "template_path": "pages/opportunities/statistics.html",
        "title": "Opportunity Statistics"
    },
    url="/statistics"
)

records_view = ViewConfig(
    view_class=RecordsView,
    kwargs={
        "model_class": Opportunity,
        "template_path": "pages/opportunities/records.html",
        "title": "Opportunity Records"
    },
    url="/records"
)

# Create blueprint with all views
opportunities_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=Opportunity,
        form_class=OpportunityForm,
        service=opportunity_service,
        views={
            "dashboard": dashboard_view,
            "filtered": filtered_view,
            "statistics": statistics_view,
            "records": records_view
        }
    )
)