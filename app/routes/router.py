def register_routes(app):
    """Register all routes with the application."""
    from routes.web.main import register_routes as register_main_routes
    from routes.web.companies import register_routes as register_company_web
    from routes.api.companies import register_routes as register_company_api
    # Import all other route registration functions

    # Register web routes
    register_main_routes(app)
    register_company_web(app)

    # Register API routes
    register_company_api(app)

    # Register all other routes...