# app/routes/api/json_utils.py

from functools import wraps

from flask import jsonify
from werkzeug.exceptions import HTTPException

from app.utils.app_logging import get_logger

logger = get_logger()


def json_endpoint(f):
    """
    Wrap a view to return a uniform JSON response:
      - on success: { success: true, data: ... }
      - on HTTPException: { success: false, error: message }, status=code
      - on other Exception: { success: false, error: 'Internal server error' }, status=500
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            # allow view to return (payload, status) or just payload
            if isinstance(result, tuple):
                payload, status = result
            else:
                payload, status = result, 200
            return jsonify({"success": True, "data": payload}), status
        except HTTPException as he:
            # abort(404, "msg") and similar
            return jsonify({"success": False, "error": he.description}), he.code
        except Exception as e:
            logger.exception(f"Unhandled exception in {f.__name__}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    return wrapped
