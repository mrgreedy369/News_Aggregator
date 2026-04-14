from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('news.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Invalid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        # Check uniqueness
        if not errors:
            if User.get_by_email(email):
                errors.append('Email already registered.')
            elif User.get_by_username(username):
                errors.append('Username already taken.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'register.html',
                username=username,
                email=email,
                full_name=full_name
            )

        # Import bcrypt inside function to avoid circular imports
        from app import bcrypt
        user = User.create(bcrypt, username, email, password, full_name)

        if user:
            login_user(user)
            flash(f'Welcome to NewsHub, {username}! 🎉', 'success')
            return redirect(url_for('news.dashboard'))
        else:
            flash('Registration failed. Please try again.', 'danger')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('news.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html', email=email)

        user = User.get_by_email(email)

        if user:
            from app import bcrypt
            if user.check_password(bcrypt, password):
                login_user(user, remember=bool(remember))
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.username}! 👋', 'success')
                return redirect(next_page if next_page else url_for('news.dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))