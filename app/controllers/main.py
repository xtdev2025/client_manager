from datetime import datetime, timedelta

from flask import Blueprint, redirect, url_for
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
    return MainView.render_index()


@main.route("/dashboard")
@login_required
def dashboard():
    """Dashboard route"""
    from app.models.template import Template

    user = User.get_by_id(current_user.id)
    user_type = user.get("user_type", "client") if user else "client"

    # Admin dashboard
    if user_type == "admin":
        clients = Client.get_all()
        admins = Admin.get_all()
        plans = Plan.get_all()
        domains = Domain.get_all()
        infos = Info.get_all()
        templates = Template.get_all()
        recent_login_logs = LoginLog.get_recent()
        client_lookup = {client["_id"]: client for client in clients}
        infos_detailed = []
        for info in infos:
            client_obj = client_lookup.get(info.get("client_id"))
            infos_detailed.append(
                {
                    "id": str(info.get("_id")),
                    "agencia": info.get("agencia"),
                    "conta": info.get("conta"),
                    "saldo": info.get("saldo", 0.0),
                    "status": info.get("status", "unknown"),
                    "updatedAt": info.get("updatedAt"),
                    "client_username": client_obj.get("username") if client_obj else "Desconhecido",
                    "client_status": client_obj.get("status") if client_obj else None,
                }
            )
        client_count = len(clients)
        admin_count = len(admins)
        plan_count = len(plans)
        domain_count = len(domains)
        info_count = len(infos)
        template_count = len(templates)

        # Calculate active vs inactive clients
        active_clients = len([c for c in clients if c.get("status") == "active"])

        # Calculate active vs inactive infos
        active_infos = len([i for i in infos if i.get("status") == "active"])

        return MainView.render_dashboard(
            user,
            user_type="admin",
            client_count=client_count,
            admin_count=admin_count,
            plan_count=plan_count,
            domain_count=domain_count,
            info_count=info_count,
            template_count=template_count,
            active_clients=active_clients,
            active_infos=active_infos,
            recent_login_logs=recent_login_logs,
            infos_detailed=infos_detailed,
        )

    # Client dashboard
    else:
        # Get plan details if client has one
        plan = None
        expiration_date = None

        if user and user.get("plan_id"):
            plan = Plan.get_by_id(user.get("plan_id"))

        if user and user.get("plan_id") and plan and plan.get("duration_days"):
            activation_candidate = (
                user.get("planActivatedAt") or user.get("updatedAt") or user.get("createdAt")
            )
            if isinstance(activation_candidate, datetime):
                if not user.get("planActivatedAt"):
                    user["planActivatedAt"] = activation_candidate
                if not user.get("expiredAt"):
                    user["expiredAt"] = activation_candidate + timedelta(
                        days=plan.get("duration_days")
                    )
                expiration_date = user.get("expiredAt")

        # Get client domains
        client_domains = []
        if user:
            client_domains = Domain.get_client_domains(user["_id"])

        # Get client infos
        client_infos = []
        if user:
            client_infos = Info.get_by_client(user["_id"])

        # Calculate counts for statistics
        active_infos = sum(1 for info in client_infos if info.get("is_active", False))
        info_count = len(client_infos)

        return MainView.render_dashboard(
            user,
            user_type="client",
            plan=plan,
            client_domains=client_domains,
            client_infos=client_infos,
            active_infos=active_infos,
            info_count=info_count,
            now=datetime.utcnow(),
            navbar_plan_expiration=expiration_date,
        )
