from app.models.pages.company import Company
from app.forms.company import CompanyForm
from app.services.company import CompanyService
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.views.base_views import DashboardView, FilteredView, StatisticsView, RecordsView

# Create service
company_service = CompanyService()

# Configure views
dashboard_view = ViewConfig(
    view_class=DashboardView,
    kwargs={
        "template_path": "pages/companies/dashboard.html",
        "title": "Companies Dashboard"
    },
    endpoint="dashboard"
)

filtered_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/companies/filtered.html",
        "title": "Filtered Companies"
    },
    url="/filtered"
)

statistics_view = ViewConfig(
    view_class=StatisticsView,
    kwargs={
        "template_path": "pages/companies/statistics.html",
        "title": "Company Statistics"
    },
    url="/statistics"
)

records_view = ViewConfig(
    view_class=RecordsView,
    kwargs={
        "model_class": Company,
        "template_path": "pages/companies/records.html",
        "title": "Company Records"
    },
    url="/records"
)

# Create blueprint with all views
companies_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=Company,
        form_class=CompanyForm,
        service=company_service,
        views={
            "dashboard": dashboard_view,
            "filtered": filtered_view,
            "statistics": statistics_view,
            "records": records_view
        }
    )
)