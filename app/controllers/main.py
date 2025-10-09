from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app.models.client import Client
from app.models.admin import Admin
from app.models.plan import Plan
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
    user = User.get_by_id(current_user.id)
    user_type = user.get('user_type', 'client') if user else 'client'
    
    # Admin dashboard
    if user_type == 'admin':
        client_count = len(Client.get_all())
        admin_count = len(Admin.get_all())
        plan_count = len(Plan.get_all())
        
        return MainView.render_dashboard(
            user,
            client_count=client_count,
            admin_count=admin_count,
            plan_count=plan_count
        )
    
    # Client dashboard
    else:
        # Get plan details if client has one
        plan = None
        if user and user.get('plan_id'):
            plan = Plan.get_by_id(user.get('plan_id'))
            
        return MainView.render_dashboard(
            user,
            plan=plan
        )