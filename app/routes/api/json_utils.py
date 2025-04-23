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

            # Convert APIContext objects to dicts
            if hasattr(payload, "to_dict"):
                payload = payload.to_dict()

            return jsonify({"success": True, "data": payload}), status

        except HTTPException as he:
            return jsonify({"success": False, "error": he.description}), he.code
        except Exception:
            logger.exception(f"Unhandled exception in {f.__name__}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    return wrapped
