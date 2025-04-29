# app/routes/web/context_utils.py

from functools import wraps
from typing import Any, Type

from flask import g, current_app


def use_context(context_cls: Type[Any], *ctx_args, **ctx_kwargs):
    """
    Decorator to build a context object and inject it into the view.

    Args:
        context_cls: The Context class to instantiate (e.g. TableWebContext).
        *ctx_args, **ctx_kwargs: Passed to the context_cls constructor.
    """

    def decorator(view_fn):
        @wraps(view_fn)
        def wrapped(*args, **kwargs):
            # If this is an TableWebContext, handle the entity parameter
            if context_cls.__name__ == "TableWebContext":
                entity_id = kwargs.get("entity_id")
                entity_table_name = ctx_kwargs.get("entity_table_name")

                # For create action, use empty entity
                if ctx_kwargs.get("action") == "create":
                    ctx_kwargs["entity"] = {}
                # For view/edit actions, fetch entity
                elif entity_id and entity_table_name:
                    from app.utils.model_registry import get_model_by_name
                    from app.services.crud_service import CRUDService

                    model_class = get_model_by_name(entity_table_name)
                    service = CRUDService(model_class)

                    try:
                        entity = service.get_by_id(entity_id)
                        ctx_kwargs["entity"] = entity
                    except Exception as e:
                        current_app.logger.error(f"Error fetching entity: {str(e)}")
                        ctx_kwargs["entity"] = {}
                else:
                    ctx_kwargs["entity"] = {}

                # Pass entity_id to context
                if entity_id:
                    ctx_kwargs["entity_id"] = entity_id

            # Instantiate the context
            ctx = context_cls(*ctx_args, **ctx_kwargs)
            # Store on flask.g if you ever need it elsewhere
            g.context = ctx
            # Call the view, injecting as keyword arg
            return view_fn(*args, context=ctx, **kwargs)

        return wrapped

    return decorator
