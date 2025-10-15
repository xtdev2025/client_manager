from functools import wraps
from typing import Any, Callable

from flask import Blueprint, flash, redirect, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import limiter
from app.models.admin import Admin
from app.models.client import Client
from app.models.user import User
from app.services.audit_helper import log_change, log_creation
from app.services.auth_service import AuthService
from app.views.auth_view import AuthView

auth = Blueprint("auth", __name__, url_prefix="/auth")


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for routes that require admin access"""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        user = User.get_by_id(current_user.id)
        if not user or "role" not in user or user["role"] not in ["admin", "super_admin"]:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


def super_admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for routes that require super admin access"""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        user = User.get_by_id(current_user.id)
        if not user or "role" not in user or user["role"] != "super_admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


@auth.route("/login", methods=["GET", "POST"])
# @limiter.limit("10 per minute")
def login():
    """Login route with rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Use AuthService for authentication
        success, user, error_message = AuthService.authenticate_user(username, password)

        if not success:
            flash(error_message, "danger")
            return AuthView.render_login(form_data={"username": username})

        # Store user type and role in session
        session["user_type"] = user.get("user_type", "client")
        session["role"] = user.get("role", "client")

        # Create a User object for Flask-Login
        from app.utils.user_loader import UserObject

        user_obj = UserObject(str(user["_id"]))
        login_user(user_obj, remember=True)

        # Log the successful login
        AuthService.log_login_attempt(
            user_id=str(user["_id"]),
            username=user.get("username"),
            success=True,
            role=user.get("role", "client"),
            user_type=user.get("user_type", "client"),
        )

        next_page = request.args.get("next")
        if next_page and not next_page.startswith('/'):
            next_page = None
        flash("Login successful!", "success")
        return redirect(next_page if next_page else url_for("main.dashboard"))

    return AuthView.render_login()


@auth.route("/logout")
@login_required
def logout():
    """Logout route"""
    # Log logout before clearing session
    user_id = current_user.id if current_user.is_authenticated else None
    username = (
        current_user.user.get("username", "unknown")
        if current_user.is_authenticated and current_user.user
        else "unknown"
    )

    if user_id:
        log_change("admin", "logout", entity_id=str(user_id), payload={"username": username})

    logout_user()
    session.pop("user_type", None)
    session.pop("role", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register route for clients"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            flash("Please fill out all fields", "danger")
            return AuthView.render_register(form_data={"username": username})

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return AuthView.render_register(form_data={"username": username})

        # Check if username already exists
        if User.get_by_username(username):
            flash("Username already exists", "danger")
            return AuthView.render_register(form_data={"username": username})

        # Create client with default plan (None for now)
        success, message = Client.create(username, password, None)

        if success:
            flash("Registration successful! You can now login.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(f"Registration failed: {message}", "danger")

    return AuthView.render_register()


@auth.route("/register_admin", methods=["GET", "POST"])
@login_required
@super_admin_required
@limiter.limit("5 per minute")
def register_admin():
    """Register route for admins (only accessible by super_admin) with rate limiting"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role", "admin")

        if not username or not password or not confirm_password:
            flash("Please fill out all fields", "danger")
            return AuthView.render_register_admin(form_data={"username": username})

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return AuthView.render_register_admin(form_data={"username": username, "role": role})

        # Use AuthService for validation
        valid, error = AuthService.validate_registration_data(username, password)
        if not valid:
            flash(error, "danger")
            return AuthView.render_register_admin(form_data={"username": username, "role": role})

        # Create admin
        success, message = Admin.create(username, password, role)

        if success:
            # Log the admin creation in audit trail
            log_creation(
                "admin",
                entity_id=message,
                payload={"username": username, "role": role},
            )
            flash("Admin registration successful!", "success")
            return redirect(url_for("admin.list_admins"))
        else:
            flash(f"Registration failed: {message}", "danger")

    return AuthView.render_register_admin()
