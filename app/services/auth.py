# app/services/auth.py

import logging
from flask import request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app.routes.web.components.template_renderer import render_safely
from app.routes.web.context import BaseContext

logger = logging.getLogger(__name__)


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
                        next_page = url_for("home_bp.index")
                        logger.info(f"Redirecting to home page at '{next_page}'")
                    except Exception as e:
                        logger.error(f"Failed to build URL for 'home.index': {e}")

                flash("Logged in successfully.", "success")
                logger.info(f"User {user.email} logged in.")
                return redirect(next_page)

            flash("Invalid email or password.", "danger")
            logger.warning(f"Failed login attempt for email: {email}")

        context = BaseContext(title="Login")
        return render_safely("pages/misc/login.html", context)

    @staticmethod
    def handle_logout():
        logout_user()
        flash("Logged out.", "info")
        logger.info("User logged out.")
        return redirect(url_for("auth_bp.login"))
