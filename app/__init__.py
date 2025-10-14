import os
from datetime import datetime, timedelta

import click
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect, generate_csrf

from config import config

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
csrf = CSRFProtect()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    enabled=os.environ.get("RATELIMIT_ENABLED", "true").lower() not in ["false", "0", "no"],
)


def create_app(config_name=None, init_db=True):
    app = Flask(__name__, template_folder="templates")

    # Load the default configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "default")

    app.config.from_object(config[config_name])

    # Initialize extensions with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # Initialize user loader
    from app.utils.user_loader import init_user_loader

    init_user_loader(login_manager)

    # Register custom Jinja2 filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to <br> tags"""
        if not text:
            return ''
        from markupsafe import Markup
        return Markup(str(text).replace('\n', '<br>'))

    @app.context_processor
    def inject_csrf_token():
        """Inject CSRF token into all templates."""
        return dict(csrf_token=generate_csrf)

    @app.context_processor
    def inject_plan_metadata():
        from flask_login import current_user

        from app.models.plan import Plan

        expiration = None
        plan_duration = None
        plan_obj = None
        now = datetime.utcnow()

        if current_user.is_authenticated:
            user_data = getattr(current_user, "user", None)

            if user_data and not current_user.is_admin:
                plan_id = user_data.get("plan_id")
                expiration = user_data.get("expiredAt")
                plan_duration = None

                plan_document = None
                if plan_id:
                    plan_document = Plan.get_by_id(plan_id)
                    if plan_document:
                        plan_duration = plan_document.get("duration_days")
                        plan_obj = plan_document  # Add full plan object

                if not expiration and plan_duration:
                    activation = (
                        user_data.get("planActivatedAt")
                        or user_data.get("updatedAt")
                        or user_data.get("createdAt")
                    )
                    if isinstance(activation, datetime):
                        expiration = activation + timedelta(days=plan_duration)

        return {
            "navbar_plan_expiration": expiration,
            "navbar_plan_duration": plan_duration,
            "plan": plan_obj,  # Add plan to context
            "now": now,
        }

    # Register blueprints
    from app.controllers.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from app.controllers.client import client as client_blueprint

    app.register_blueprint(client_blueprint)

    from app.controllers.admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint)

    from app.controllers.plan import plan as plan_blueprint

    app.register_blueprint(plan_blueprint)

    from app.controllers.template import template as template_blueprint

    app.register_blueprint(template_blueprint)

    from app.controllers.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from app.controllers.domain import domain as domain_blueprint

    app.register_blueprint(domain_blueprint)

    from app.controllers.info import info as info_blueprint

    app.register_blueprint(info_blueprint)

    from app.views.client_domain_view import client_domain_bp

    app.register_blueprint(client_domain_bp)

    from app.controllers.dashboard import dashboard as dashboard_blueprint

    app.register_blueprint(dashboard_blueprint)

    from app.controllers.payout import payout as payout_blueprint

    app.register_blueprint(payout_blueprint)

    # Initialize database with default data if needed
    # Handle CSRF errors
    @app.errorhandler(400)
    def handle_csrf_error(e):
        if 'CSRF' in str(e):
            from flask import flash, redirect, url_for
            flash('Sua sessão expirou. Por favor, tente novamente.', 'danger')
            return redirect(url_for('auth.login'))
        return e

    # Only initialize database if init_db is True
    if init_db:
        with app.app_context():
            from app.db_init import initialize_db
            initialize_db()

    @app.cli.command("reconcile-payouts")
    @click.option("--limit", default=100, type=int, help="Número máximo de payouts a processar")
    @click.option("--min-delay", default=None, type=int, help="Minutos mínimos desde o requestedAt para reconciliar")
    @click.option("--interval", default=None, type=int, help="Minutos para reagendar próxima checagem")
    @click.option("--alert-attempts", default=None, type=int, help="Tentativas antes de gerar alerta")
    @click.option("--alert-age", default=None, type=int, help="Minutos desde requestedAt para gerar alerta")
    @click.option("--lookback", default=None, type=int, help="Dias de lookback para considerar payouts")
    def reconcile_payouts_command(limit, min_delay, interval, alert_attempts, alert_age, lookback):
        """Executa reconciliação de payouts Heleket pendentes."""
        from app.services.payout_reconciliation_service import PayoutReconciliationService

        results = PayoutReconciliationService.schedule_pending(
            limit=limit,
            min_delay_minutes=min_delay,
            poll_interval_minutes=interval,
            alert_attempts=alert_attempts,
            alert_age_minutes=alert_age,
            lookback_days=lookback,
        )

        click.echo(
            "Reconciliation summary: "
            f"checked={results['checked']} finalized={results['finalized']} "
            f"alerts={results['alerts']} errors={results['errors']}"
        )

    return app
