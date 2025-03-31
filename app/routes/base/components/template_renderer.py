import logging
import traceback
from typing import Union
from flask import render_template, current_app, request
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from app.routes.base.components.form_handler import BasicContext, ResourceContext, TableContext

logger = logging.getLogger(__name__)


def render_safely(
        template_name: str,
        context: Union[BasicContext, TableContext, ResourceContext],
        fallback_error_message: str = "An error occurred while rendering the page",
        endpoint_name: str = None,
):
    current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
    current_path = request.path

    try:
        logger.debug(f"🔍 Rendering template: {template_name} for {current_endpoint} ({current_path})")
        # Log the context being passed into the template to check for unexpected fields
        logger.debug(f"🔧 Context Data: {context}")

        # Log the successful pageview here
        logger.info(
            f"Pageview: Successfully rendered template: {template_name} for {current_endpoint} ({current_path})")
        return render_template(template_name, **context.__dict__)
    except (TemplateNotFound, TemplateSyntaxError, Exception) as e:
        if isinstance(e, TemplateNotFound):
            error_type = "Template Not Found"
            details = f"The template '{e.name}' could not be found."
            status_code = 404
        elif isinstance(e, TemplateSyntaxError):
            error_type = "Template Syntax Error"
            details = f"Syntax error in template '{template_name}': {str(e)}"
            status_code = 500
        else:
            error_type = "Rendering Error"
            details = str(e)
            status_code = 500

        logger.error(
            f"{__name__} - ERROR - {error_type} in '{template_name}' " f"for {current_endpoint} ({current_path}): {details}")

        # Log additional context data for error identification
        logger.debug(f"🔧 Error Context Data: {context}")

        if current_app.debug:
            logger.debug(f"Traceback:\n{traceback.format_exc()}")

        context.error_message = f"{error_type}: {details}" if current_app.debug else fallback_error_message

        try:
            logger.debug(f"🔁 Fallback render attempt for: {template_name}")
            return render_template(template_name, **context.__dict__), status_code
        except Exception as e2:
            logger.critical(
                f"{__name__} - CRITICAL - Failed to re-render '{template_name}' with error context: {e2} "
                "for {current_endpoint} ({current_path})"
            )
            return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code
