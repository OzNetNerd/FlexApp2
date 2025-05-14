from app.models.pages.task import Task
from app.forms.task import TaskForm
from app.services.task import TaskService
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.views.base_view import DashboardView, FilteredView, StatisticsView, RecordsView

# Create service
task_service = TaskService()

# Configure views
dashboard_view = ViewConfig(
    view_class=DashboardView,
    kwargs={
        "template_path": "pages/tasks/dashboard.html",
        "title": "Tasks Dashboard"
    },
    endpoint="dashboard"
)

filtered_view = ViewConfig(
    view_class=FilteredView,
    kwargs={
        "template_path": "pages/tasks/filtered.html",
        "title": "Filtered Tasks"
    },
    url="/filtered"
)

statistics_view = ViewConfig(
    view_class=StatisticsView,
    kwargs={
        "template_path": "pages/tasks/statistics.html",
        "title": "Task Statistics"
    },
    url="/statistics"
)

records_view = ViewConfig(
    view_class=RecordsView,
    kwargs={
        "model_class": Task,
        "template_path": "pages/tasks/records.html",
        "title": "Task Records"
    },
    url="/records"
)

# Create blueprint with all views
tasks_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=Task,
        form_class=TaskForm,
        service=task_service,
        url_prefix="/tasks",
        views={
            "dashboard": dashboard_view,
            "filtered": filtered_view,
            "statistics": statistics_view,
            "records": records_view
        }
    )
)