from flask import request
from flask_login import login_required
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext, TableContext
from app.utils.app_logging import get_logger
from datetime import datetime
import json

logger = get_logger()


class BaseView:
    """Base class for all views."""

    def __init__(self, blueprint, service, template_path, title=None, read_only=True):
        self.blueprint = blueprint
        self.service = service
        self.template_path = template_path
        self.title = title
        self.read_only = read_only

    def register(self, url="/", endpoint=None, methods=None):
        """Register this view with the blueprint."""
        if methods is None:
            methods = ["GET"]
        endpoint = endpoint or self.__class__.__name__.lower()
        self.blueprint.add_url_rule(
            url,
            endpoint=endpoint,
            view_func=login_required(self.dispatch),
            methods=methods
        )

    def get_context(self, **kwargs):
        """Get context for rendering templates."""
        return WebContext(title=self.title, read_only=self.read_only, **kwargs)

    def dispatch(self):
        """Handle the request."""
        raise NotImplementedError("Subclasses must implement dispatch method")

    def render(self, context, error_message=None):
        """Render template with context."""
        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=error_message or f"Error rendering {self.title}",
            endpoint_name=request.endpoint,
        )
        return render_safely(config)


class DashboardView(BaseView):
    """View for dashboard pages."""

    def dispatch(self):
        """Handle dashboard requests."""
        stats = self.service.get_dashboard_statistics()
        context = self.get_context(stats=stats)
        return self.render(context)


class FilteredView(BaseView):
    """View for filtered list pages."""

    def dispatch(self):
        """Handle filtered list requests."""
        filters = request.args.to_dict()
        entities = self.service.get_filtered_entities(filters)
        context = self.get_context(entities=entities, filters=filters)
        return self.render(context)


class StatisticsView(BaseView):
    """View for statistics pages."""

    def dispatch(self):
        """Handle statistics requests."""
        stats = self.service.get_statistics()
        context = self.get_context(**stats)
        return self.render(context)


class RecordsView(BaseView):
    """View for records/table views."""

    def __init__(self, blueprint, service, model_class, template_path, title=None):
        super().__init__(blueprint, service, template_path, title)
        self.model_class = model_class

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def dispatch(self):
        """Handle record list requests."""
        filters = request.args.to_dict()
        entities = self.service.get_filtered_entities(filters)
        table_data = [entity.to_dict() for entity in entities]
        json_data = json.dumps(table_data, default=self.json_serial)

        context = TableContext(
            model_class=self.model_class,
            read_only=self.read_only,
            action="view",
            show_heading=True,
            table_data=json_data
        )
        return self.render(context)

class CompanyFilteredView(FilteredView):
    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        # Rename entities to match template expectations
        context.companies = context.entities
        del context.entities
        return context

class ContactFilteredView(FilteredView):
    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context.contacts = context.entities
        del context.entities
        return context

class OpportunityFilteredView(FilteredView):
    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context.opportunities = context.entities
        del context.entities
        return context