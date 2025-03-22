from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app.models import User


def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Make session permanent
            from flask import session
            session.permanent = True

            # Remember user setting (optional)
            remember = request.form.get('remember', False)
            login_user(user, remember=remember)

            # Redirect to the next page or default
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')

            flash('Logged in successfully.', 'success')
            return redirect(next_page)

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth_bp.login'))

def load_user(user_id):
    return User.query.get(int(user_id))