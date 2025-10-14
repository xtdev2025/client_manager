from datetime import datetime

from flask import Blueprint, current_app, jsonify, redirect, url_for
from flask_login import current_user, login_required

from app.models.plan import Plan
from app.views import MainView

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Home page route"""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    plans = Plan.get_all()
    return MainView.render_index(plans=plans)


@main.route("/dashboard")
@login_required
def dashboard():
    """Dashboard route - redirect to new enterprise dashboard"""
    return redirect(url_for("dashboard.index"))


@main.route("/health")
def health_check():
    """Lightweight health-check endpoint used by deployment targets."""
    return jsonify(
        {
            "status": "ok",
            "webhook_secret_configured": bool(
                current_app.config.get("HELEKET_WEBHOOK_SECRET")
            ),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )


@main.route("/login", methods=["GET", "POST"])
def login():
    """Redirect to auth login for convenience"""
    return redirect(url_for("auth.login"))


@main.route("/logout")
def logout():
    """Redirect to auth logout for convenience"""
    return redirect(url_for("auth.logout"))
