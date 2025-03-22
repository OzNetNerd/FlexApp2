from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from models import User


def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))  # Adjust as needed

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth_bp.login'))

def load_user(user_id):
    return User.query.get(int(user_id))