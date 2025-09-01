from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .utils import validate_email, validate_name, validate_password, generate_username_from_name
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST' and request.form.get('form_type') == 'signup':
        f_name = request.form.get('first_name', '').strip()
        l_name = request.form.get('last_name', '').strip()
        email = request.form.get('signin_email', '').strip().lower()
        password = request.form.get('signin_password', '')
        confirmed_password = request.form.get('confirmed_password', '')

        errors = []

        # Validate first name
        is_valid, error_msg = validate_name(f_name, "First name")
        if not is_valid:
            errors.append(error_msg)

        # Validate last name
        is_valid, error_msg = validate_name(l_name, "Last name")
        if not is_valid:
            errors.append(error_msg)

        # Validate email
        if not validate_email(email):
            errors.append("Please enter a valid email address")

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            errors.append("Email address is already registered")

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            errors.append(error_msg)

        # Validate password confirmation
        if password != confirmed_password:
            errors.append("Passwords do not match")

        if errors:
            # Display errors to user
            for error in errors:
                flash(error, 'error')
            print(f"Validation errors: {errors}")
        else:
            try:
                # Generate username from name
                username = generate_username_from_name(f_name, l_name)
                if not username:
                    username = f"{f_name.lower()}{l_name.lower()}"[:15]  # Fallback

                # Hash password
                pw_hash = generate_password_hash(password)

                # Create new user with correct parameters
                new_user = User(
                    email=email,
                    username=username,
                    password_hash=pw_hash,
                    f_name=f_name,
                    l_name=l_name,
                )

                # Add to database
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully!", 'success')

                # Login user with remember=True
                login_user(new_user, remember=True)
                new_user.update_last_login()

                return redirect(url_for('views.home'))

            except Exception as e:
                db.session.rollback()
                print(f"Error creating user: {e}")
                flash("An error occurred while creating your account. Please try again.", 'error')

    elif request.method == 'POST' and request.form.get('form_type') == 'login':
        email = request.form.get('login_email', '').strip().lower()
        password = request.form.get('login_password', '')
        remember = request.form.get('remember_me', False)  # Get remember me checkbox
        errors = []

        # Validate email
        if not validate_email(email):
            errors.append("Please enter a valid email address")

        # Validate password
        if not password:
            errors.append("Password is required")

        if not errors:
            # Check credentials - look for user by email OR username
            user = User.query.filter((User.email == email) | (User.username == email)).first()

            if not user:
                errors.append("Invalid email or password")
            elif not check_password_hash(user.password_hash, password):
                errors.append("Invalid email or password")
            elif not user.is_active:
                errors.append("Your account has been deactivated. Please contact support.")

        if errors:
            # Display errors to user
            for error in errors:
                flash(error, 'error')
        else:
            try:
                # All validation passed - proceed with login
                login_user(user, remember=bool(remember))  # Use remember checkbox or default True
                user.update_last_login()
                flash("Login successful!", 'success')

                # Handle next parameter for redirecting after login
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('views.home'))

            except Exception as e:
                print(e)
                flash("An error occurred during login. Please try again.", 'error')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", 'success')
    return redirect(url_for('auth.login'))
