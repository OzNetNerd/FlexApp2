# app/routes/web/context_utils.py

from functools import wraps
from typing import Any, Type

from flask import g


def use_context(context_cls: Type[Any], *ctx_args, **ctx_kwargs):
    """
    Decorator to build a context object and inject it into the view.

    Args:
        context_cls: The Context class to instantiate (e.g. TableContext).
        *ctx_args, **ctx_kwargs: Passed to the context_cls constructor.
    """

    def decorator(view_fn):
        @wraps(view_fn)
        def wrapped(*args, **kwargs):
            # Instantiate the context
            ctx = context_cls(*ctx_args, **ctx_kwargs)
            # Store on flask.g if you ever need it elsewhere
            g.context = ctx
            # Call the view, injecting as keyword arg
            return view_fn(*args, context=ctx, **kwargs)

        return wrapped

    return decorator
