import logging
from typing import Any

logger = logging.getLogger(__name__)


def data_route(ctx: Any) -> Any:
    """
    Handle API requests for table data.

    Logs the request and delegates handling to the data route handler.

    Args:
        ctx (Any): The class instance containing request_logger, model, and data_handler.

    Returns:
        Any: The data response for the table.
    """
    ctx.request_logger.log_request_info(ctx.model.__name__, "data")
    return ctx.data_handler.handle_data_request()
