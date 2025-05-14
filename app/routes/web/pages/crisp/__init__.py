from flask import flash, redirect, url_for, request
from flask_login import login_required
from app.models import Crisp, db
from app.utils.app_logging import get_logger
from app.routes.web.utils.blueprint_factory import BlueprintConfig, ViewConfig, create_crud_blueprint
from app.routes.web.pages.crisp.views import CrispDashboardView, CrispScoresView, CrispDetailView, CrispFormView, CrispComparisonView
from app.services.crisp import CrispService

logger = get_logger()

# Create service instance
crisp_service = CrispService()

# Configure views
dashboard_view = ViewConfig(
    view_class=CrispDashboardView,
    kwargs={
        "template_path": "pages/crisp/dashboard.html",
        "title": "CRISP Score Dashboard",
        "service": crisp_service
    },
    endpoint="dashboard"
)

# [Rest of the view configurations]

# Create blueprint with all views
crisp_bp = create_crud_blueprint(
    BlueprintConfig(
        model_class=Crisp,
        service=crisp_service,
        url_prefix="/crisp",
        views={
            "dashboard": dashboard_view,
            "scores": scores_view,
            "detail": detail_view,
            "create": create_view,
            "edit": edit_view,
            "comparison": comparison_view
        }
    )
)

# Additional routes for form submissions
@crisp_bp.route("/score/<int:relationship_id>", methods=["POST"])
@login_required
def submit(relationship_id):
    success, message = crisp_service.create_score(request.form)
    flash(message, "success" if success else "danger")
    return redirect(url_for("crisp_bp.dashboard"))

@crisp_bp.route("/submit-new", methods=["POST"])
@login_required
def submit_new():
    success, message = crisp_service.create_score(request.form)
    flash(message, "success" if success else "danger")
    return redirect(url_for("crisp_bp.dashboard"))

logger.info("Successfully set up CRISP Score routes.")