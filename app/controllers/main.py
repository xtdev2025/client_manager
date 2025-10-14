from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, redirect, url_for
from flask_login import current_user, login_required

from app.models.admin import Admin
from app.models.client import Client
from app.models.domain import Domain
from app.models.info import Info
from app.models.login_log import LoginLog
from app.models.plan import Plan
from app.models.user import User
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
