from flask import render_template
from app.utils.app_logging import get_logger

logger = get_logger()


class AuthViewService:
    def render_login_template(self):
        """Render the login template."""
        try:
            return render_template("pages/misc/login.html", title="Login")
        except Exception as e:
            logger.exception(f"Template error: {e}")
            return f"<h1>Login</h1><p>Error rendering login page: {str(e)}</p>"
