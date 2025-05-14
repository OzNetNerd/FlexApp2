from app.models.pages.user import User
from app.forms.user import UserForm
from app.services.user import UserService
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.views.base_view import DashboardView, FilteredView, StatisticsView, RecordsView

# Create service
user_service = UserService()

# Configure views
dashboard_view = ViewConfig(
    view_class=DashboardView,
    kwargs={
        "template_path": "pages/users/dashboard.html",
        "title": "Users Dashboard"
    },
    endpoint="dashboard"
)

filtered_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/users/filtered.html",
        "title": "Filtered Users"
    },
    url="/filtered"
)

statistics_view = ViewConfig(
    view_class=StatisticsView,
    kwargs={
        "template_path": "pages/users/statistics.html",
        "title": "User Statistics"
    },
    url="/statistics"
)

records_view = ViewConfig(
    view_class=RecordsView,
    kwargs={
        "model_class": User,
        "template_path": "pages/users/records.html",
        "title": "User Records"
    },
    url="/records"
)

# Create blueprint with all views
users_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=User,
        form_class=UserForm,
        service=user_service,
        views={
            "dashboard": dashboard_view,
            "filtered": filtered_view,
            "statistics": statistics_view,
            "records": records_view
        }
    )
)