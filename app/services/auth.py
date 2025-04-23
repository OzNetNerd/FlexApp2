# app/services/auth.py

from flask import request, redirect, url_for, flash, session, render_template
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from app.utils.app_logging import get_logger

logger = get_logger()


class AuthService:
    def __init__(self, model):
        self.model = model

    def handle_login(self):
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            logger.info(f"Attempting login for email: {email}")

            user = self.model.query.filter_by(email=email).first()

            if user and check_password_hash(user.password_hash, password):
                logger.info(f"Password valid for user: {user.email}")
                session.permanent = True
                login_user(user, remember=True)

                next_page = request.args.get("next")
                if not next_page or not next_page.startswith("/"):
                    try:
                        next_page = url_for("home.index")  # Changed from home_bp.index
                        logger.info(f"Redirecting to home page at '{next_page}'")
                    except Exception as e:
                        logger.error(f"Failed to build URL for 'home.index': {e}")
                        next_page = "/"  # Fallback to root

                flash("Logged in successfully.", "success")
                logger.info(f"User {user.email} logged in.")
                return redirect(next_page)

            flash("Invalid email or password.", "danger")
            logger.warning(f"Failed login attempt for email: {email}")

        # Use direct Flask render_template for simplicity
        try:
            return render_template("pages/misc/login.html", title="Login")
        except Exception as e:
            logger.exception(f"Template error: {e}")
            return f"<h1>Login</h1><p>Error rendering login page: {str(e)}</p>"

    @staticmethod
    def handle_logout():
        logout_user()
        flash("Logged out.", "info")
        logger.info("User logged out.")
        return redirect(url_for("auth.login"))  # Changed from auth_bp.login
