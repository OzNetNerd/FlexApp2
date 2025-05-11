# from flask import render_template, request
# from flask_login import login_required
# from app.models.pages.company import Company
# from app.models.base import db
# from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
# from app.routes.web.utils.context import TableContext
# from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
# from app.services.company_service import CompanyService
#
# # Create the blueprint with the Company model
# companies_bp = create_crud_blueprint(BlueprintConfig(model_class=Company))
# company_service = CompanyService()
#
#
# @companies_bp.route("/", methods=["GET"], endpoint="index")
# @login_required
# def companies_dashboard():
#     # Get statistics and data from service
#     stats = company_service.get_dashboard_stats()
#     top_companies = company_service.get_top_companies()
#     segments = company_service.get_engagement_segments()
#     growth_data = company_service.prepare_growth_data()
#
#     return render_template(
#         "pages/companies/dashboard.html",
#         stats=stats,
#         segments=segments,
#         top_companies=top_companies,
#         growth_data=growth_data
#     )
#
#
# @companies_bp.route("/filtered", methods=["GET"])
# @login_required
# def filtered_companies():
#     # Get filter parameters
#     filters = {
#         "has_opportunities": request.args.get("has_opportunities"),
#         "has_contacts": request.args.get("has_contacts"),
#         "has_capabilities": request.args.get("has_capabilities")
#     }
#
#     # Get filtered companies from service
#     companies = company_service.get_filtered_companies(filters)
#
#     return render_template(
#         "pages/companies/filtered.html",
#         companies=companies,
#         filters=filters
#     )
#
#
# @companies_bp.route("/statistics", methods=["GET"])
# @login_required
# def statistics():
#     # Get statistics from service
#     stats = company_service.get_statistics()
#
#     return render_template(
#         "pages/companies/statistics.html",
#         total_companies=stats["total_companies"],
#         with_opportunities=stats["with_opportunities"],
#         with_contacts=stats["with_contacts"],
#         no_engagement=stats["no_engagement"]
#     )
#
#
# @companies_bp.route("/view2", methods=["GET"])
# @login_required
# def view2():
#     return render_template(
#         "pages/companies/view.html",
#         id=0,  # Add id parameter
#         model_name="Company",  # These parameters are likely needed too
#         entity_name="Demo Company",
#         read_only=True,
#         submit_url="#",  # For the form action
#         csrf_input=""  # For CSRF protection
#     )
#
#
# @companies_bp.route("/records", methods=["GET"])
# @login_required
# def records():
#     # Create appropriate context for the records view
#     context = TableContext(
#         model_class=Company,
#         read_only=True,
#         action="view",
#         show_heading=True
#     )
#
#     # Configure the render_safely call
#     config = RenderSafelyConfig(
#         template_path="pages/companies/records.html",
#         context=context,
#         error_message="An error occurred while rendering the companies records page",
#         endpoint_name=request.endpoint
#     )
#
#     # Return the safely rendered template
#     return render_safely(config)