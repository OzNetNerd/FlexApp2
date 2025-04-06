import logging
from flask import Blueprint, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from app.models import User
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import BaseContext

logger = logging.getLogger(__name__)

# Define the auth blueprint with a URL prefix
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle login form submission and authentication.

    On POST:
        - Authenticates user by email and password.
        - Sets session and remember token.
        - Redirects to intended page or main index.

    On GET:
        - Renders login page.

    Returns:
        Response: Flask response (redirect or rendered template).
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        logger.debug(f"Attempting login for email: {email}")

        user = User.query.filter_by(email=email).first()

        if user:
            logger.debug(f"User found: {user.email}")
        else:
            logger.debug(f"User not found for email: {email}")

        if user and check_password_hash(user.password_hash, password):
            logger.debug(f"Password valid for user: {user.email}")
            session.permanent = True
            login_user(user, remember=True)

            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("main.index")

            flash("Logged in successfully.", "success")
            logger.info(f"User {user.email} logged in.")
            return redirect(next_page)

        flash("Invalid email or password.", "danger")
        logger.warning(f"Failed login attempt for email: {email}")

    context = BaseContext(title="Login")
    return render_safely("pages/misc/login.html", context)


@auth_bp.route("/logout")
def logout():
    """Logs out the current user and redirects to login.

    Returns:
        Response: Redirect to login page with flash message.
    """
    logout_user()
    flash("Logged out.", "info")
    logger.info("User logged out.")
    return redirect(url_for("auth_bp.login"))


logger.info("Auth routes setup successfully.")
