from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app.models import User
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth_bp", __name__)


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

        if user and check_password_hash(user.password_hash, password):
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

    return render_template("login.html")


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
