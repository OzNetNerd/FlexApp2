from flask import flash, redirect, request
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.auth.core import AuthCoreService
from app.services.auth.session import SessionService
from app.services.auth.password import PasswordService
from app.services.auth.view import AuthViewService


class AuthService(ServiceBase):
    def __init__(self, model=None):
        super().__init__(model)
        self.core = ServiceRegistry.get(AuthCoreService)
        self.core.model_class = model  # Set model class for core service
        self.session = ServiceRegistry.get(SessionService)
        self.password = ServiceRegistry.get(PasswordService)
        self.view = ServiceRegistry.get(AuthViewService)

    # Rest of the code remains the same

    def handle_login(self):
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            logger.info(f"Attempting login for email: {email}")

            user = self.core.find_user_by_email(email)

            if self.password.verify_password(user, password):
                self.session.login_user(user)
                next_page = self.session.get_next_page(request)
                flash("Logged in successfully.", "success")
                return redirect(next_page)

            flash("Invalid email or password.", "danger")
            logger.warning(f"Failed login attempt for email: {email}")

        return self.view.render_login_template()

    def handle_logout(self):
        return self.session.logout_user()