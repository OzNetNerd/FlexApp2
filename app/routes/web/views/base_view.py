"""
Base view classes for the web application.

This module defines the base view classes that other view classes in the application
can inherit from. These classes provide common functionality and structure
for handling HTTP requests.
"""


import json

from flask import request, render_template
from flask.views import MethodView
from flask_login import login_required

from app.routes.web.utils.context import WebContext, TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger

logger = get_logger()


class BaseView(MethodView):
    """Base view class for all web views.

    This class provides a foundation for other view classes to build upon,
    with common initialization and utility methods.
    """

    def __init__(self, **kwargs):
        """Initialize the base view with service and template information."""
        self.service = kwargs.get('service')
        self.template_path = kwargs.get('template_path')
        self.title = kwargs.get('title', 'Application')
        self.model_class = kwargs.get('model_class')
        self.render_config = {}
        self.context_class = WebContext
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def register(cls, blueprint, url, endpoint, **kwargs):
        """Register this view with the given blueprint."""
        view_kwargs = kwargs.get('kwargs', {})
        view_func = cls.as_view(endpoint, **view_kwargs)
        blueprint.add_url_rule(url, endpoint=endpoint, view_func=view_func)
        return view_func


class DashboardView(BaseView):
    """View class for dashboard pages.

    This class is used for rendering dashboard pages with summary statistics
    and overview information.
    """

    @login_required
    def get(self):
        """Handle GET requests for dashboard pages.

        Returns:
            HTML for the dashboard
        """
        logger.info(f"Rendering dashboard: {self.template_path}")

        # Common dashboard data preparation
        stats = self.service.get_stats() if hasattr(self.service, 'get_stats') else {}

        # Create context with default dashboard data
        context = WebContext(title=self.title)
        context.stats = stats

        # Add additional data if the service provides it
        if hasattr(self.service, 'get_dashboard_data'):
            dashboard_data = self.service.get_dashboard_data()
            for key, value in dashboard_data.items():
                setattr(context, key, value)

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render dashboard: {self.title}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class FilteredView(BaseView):
    """View class for filtered data pages.

    This class is used for rendering pages that display filtered lists
    of records based on query parameters.
    """

    @login_required
    def get(self):
        """Handle GET requests for filtered views.

        Returns:
            HTML for the filtered data view
        """
        logger.info(f"Rendering filtered view: {self.template_path}")

        # Get filter parameters from request args
        filters = request.args.to_dict()
        logger.info(f"Applied filters: {filters}")

        # Get filtered data
        if hasattr(self.service, 'get_filtered'):
            items = self.service.get_filtered(filters)
        else:
            items = self.service.get_all()

        logger.info(f"Retrieved {len(items)} items matching filter criteria")

        # Create context with filtered data
        context = WebContext(title=self.title)
        context.items = items
        context.filters = filters

        # Add additional filter-related data if available
        if hasattr(self.service, 'get_filter_options'):
            filter_options = self.service.get_filter_options()
            for key, value in filter_options.items():
                setattr(context, key, value)

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render filtered view: {self.title}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class StatisticsView(BaseView):
    """View class for statistics pages.

    This class is used for rendering pages that display detailed
    statistics and analytics.
    """

    @login_required
    def get(self):
        """Handle GET requests for statistics pages.

        Returns:
            HTML for the statistics view
        """
        logger.info(f"Rendering statistics view: {self.template_path}")

        # Get detailed statistics
        stats = {}
        if hasattr(self.service, 'get_detailed_stats'):
            stats = self.service.get_detailed_stats()
        elif hasattr(self.service, 'get_stats'):
            stats = self.service.get_stats()

        logger.info("Retrieved statistics data")

        # Create context with statistics data
        context = WebContext(title=self.title)
        context.stats = stats

        # Add additional statistics-related data if available
        if hasattr(self.service, 'get_charts_data'):
            charts_data = self.service.get_charts_data()
            for key, value in charts_data.items():
                setattr(context, key, value)

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render statistics view: {self.title}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class RecordsView(BaseView):
    """View class for table-based record views.

    This class is used for rendering pages that display records
    in a tabular format with sorting and pagination.
    """

    @login_required
    def get(self):
        """Handle GET requests for record views.

        Returns:
            HTML for the records view
        """
        logger.info(f"Rendering records view: {self.template_path}")

        # Get data from service
        items = []
        if hasattr(self.service, 'get_filtered_items'):
            items = self.service.get_filtered_items(request.args.to_dict())
        else:
            items = self.service.get_all()

        logger.info(f"Retrieved {len(items)} records")

        # Convert to dict format for table
        table_data = [item.to_dict() for item in items.items]

        # Create table context
        context = TableContext(
            model_class=self.model_class,
            read_only=True,
            action="view",
            show_heading=True,
            table_data=json.dumps(table_data)
        )

        # Configure the render_safely call
        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render records view: {self.title}",
            endpoint_name=request.endpoint,
        )

        # Return the safely rendered template
        return render_safely(config)