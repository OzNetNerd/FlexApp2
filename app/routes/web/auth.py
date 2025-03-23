from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app.models import User

auth_bp = Blueprint("auth_bp", __name__)  # ⬅️ Define the blueprint


@auth_bp.route("/login", methods=["GET", "POST"])  # ⬅️ Use blueprint route
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session.permanent = True
            remember = True  # Always remember for now
            login_user(user, remember=remember)

            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("main.index")

            flash("Logged in successfully.", "success")
            return redirect(next_page)

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")  # ⬅️ Use blueprint route
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth_bp.login"))
