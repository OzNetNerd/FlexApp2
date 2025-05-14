from app.models.pages.contact import Contact
from app.forms.contact import ContactForm  # Assuming this exists
from app.services.contact import ContactService
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.views.base_view import DashboardView, FilteredView, StatisticsView, RecordsView

# Create service
contact_service = ContactService()

# Configure views
dashboard_view = ViewConfig(
    view_class=DashboardView,
    kwargs={
        "template_path": "pages/contacts/dashboard.html",
        "title": "Contacts Dashboard"
    },
    endpoint="dashboard"
)

filtered_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/contacts/filtered.html",
        "title": "Filtered Contacts"
    },
    url="/filtered"
)

statistics_view = ViewConfig(
    view_class=StatisticsView,
    kwargs={
        "template_path": "pages/contacts/statistics.html",
        "title": "Contact Statistics"
    },
    url="/statistics"
)

records_view = ViewConfig(
    view_class=RecordsView,
    kwargs={
        "model_class": Contact,
        "template_path": "pages/contacts/records.html",
        "title": "Contact Records"
    },
    url="/records"
)

# Create blueprint with all views
contacts_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=Contact,
        form_class=ContactForm,
        service=contact_service,
        views={
            "dashboard": dashboard_view,
            "filtered": filtered_view,
            "statistics": statistics_view,
            "records": records_view
        }
    )
)