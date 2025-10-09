from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app.models.client import Client
from app.models.admin import Admin
from app.models.plan import Plan
from app.models.domain import Domain
from app.models.info import Info
from app.views import MainView

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return MainView.render_index()


@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route"""
    from app.models.template import Template

    user = User.get_by_id(current_user.id)
    user_type = user.get('user_type', 'client') if user else 'client'

    # Admin dashboard
    if user_type == 'admin':
        clients = Client.get_all()
        admins = Admin.get_all()
        plans = Plan.get_all()
        domains = Domain.get_all()
        infos = Info.get_all()
        templates = Template.get_all()

        client_count = len(clients)
        admin_count = len(admins)
        plan_count = len(plans)
        domain_count = len(domains)
        info_count = len(infos)
        template_count = len(templates)

        # Calculate active vs inactive clients
        active_clients = len([c for c in clients if c.get('status') == 'active'])

        # Calculate active vs inactive infos
        active_infos = len([i for i in infos if i.get('status') == 'active'])

        return MainView.render_dashboard(
            user,
            client_count=client_count,
            admin_count=admin_count,
            plan_count=plan_count,
            domain_count=domain_count,
            info_count=info_count,
            template_count=template_count,
            active_clients=active_clients,
            active_infos=active_infos
        )

    # Client dashboard
    else:
        # Get plan details if client has one
        plan = None
        if user and user.get('plan_id'):
            plan = Plan.get_by_id(user.get('plan_id'))

        # Get client domains
        client_domains = []
        if user:
            client_domains = Domain.get_client_domains(user['_id'])

        # Get client infos
        client_infos = []
        if user:
            client_infos = Info.get_by_client(user['_id'])

        return MainView.render_dashboard(
            user,
            plan=plan,
            client_domains=client_domains,
            client_infos=client_infos
        )
