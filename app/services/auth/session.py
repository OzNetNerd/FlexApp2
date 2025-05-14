from flask import flash, redirect, session, url_for
from flask_login import login_user, logout_user
from app.utils.app_logging import get_logger

logger = get_logger()


class SessionService:
    def login_user(self, user, remember=True):
        """Login a user and set session."""
        session.permanent = True
        login_user(user, remember=remember)
        logger.info(f"User {user.email} logged in.")

    def logout_user(self):
        """Logout the current user."""
        logout_user()
        flash("Logged out.", "info")
        logger.info("User logged out.")
        return redirect(url_for("auth_bp.login"))

    def get_next_page(self, request):
        """Get redirect target after login."""
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            try:
                next_page = url_for("home_bp.index")
                logger.info(f"Redirecting to home page at '{next_page}'")
            except Exception as e:
                logger.error(f"Failed to build URL for 'home_bp.index': {e}")
                next_page = "/"  # Fallback to root
        return next_page
