import logging
from typing import Any

from flask import url_for

from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import TableContext

logger = logging.getLogger(__name__)


def index_route(ctx: Any) -> Any:
    """
    Render the index page displaying a table of items.

    Retrieves table configuration and constructs the context for the index template,
    which is then safely rendered.

    Args:
        ctx (Any): The class instance containing request_logger, model, blueprint, etc.

    Returns:
        Any: The rendered index page.
    """
    ctx.request_logger.log_request_info(ctx.model.__name__, "index")
    table_config = ctx.table_config_manager.get_table_config(ctx.model.__tablename__)
    data_url = determine_data_url(ctx)
    context = TableContext(
        page_type="index",
        title=f"{ctx.model.__name__}s",
        table_config=table_config,
        table_id=f"{ctx.model.__tablename__}_table",
        data_url=data_url,
        entity_name=ctx.model.__name__,
        add_url=url_for(f"{ctx.blueprint.name}.create"),
        columns=table_config.get("columns", []),
    )
    return render_safely(ctx.index_template, context, f"Error rendering {ctx.model.__name__} index")


def determine_data_url(ctx: Any) -> str:
    """
    Construct the URL for table data API requests.

    Args:
        ctx (Any): The class instance containing model, blueprint, and optionally api_url_prefix.

    Returns:
        str: The URL for accessing table data.
    """
    if ctx.api_url_prefix:
        return f"{ctx.api_url_prefix}/{ctx.model.__tablename__}"
    return url_for(f"{ctx.blueprint.name}.data")
