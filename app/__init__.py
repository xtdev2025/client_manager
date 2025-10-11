from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os
from datetime import datetime, timedelta

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    enabled=True  # Will be overridden by app config if RATELIMIT_ENABLED is set
)

def create_app(config_name=None):
    app = Flask(__name__, template_folder='templates')

    # Load the default configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app.config.from_object(config[config_name])

    # Initialize extensions with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Initialize user loader
    from app.utils.user_loader import init_user_loader
    init_user_loader(login_manager)

    @app.context_processor
    def inject_plan_metadata():
        from flask_login import current_user
        from app.models.plan import Plan

        expiration = None
        plan_duration = None
        now = datetime.utcnow()

        if current_user.is_authenticated:
            user_data = getattr(current_user, 'user', None)

            if user_data and not current_user.is_admin:
                plan_id = user_data.get('plan_id')
                expiration = user_data.get('expiredAt')
                plan_duration = None

                plan_document = None
                if plan_id:
                    plan_document = Plan.get_by_id(plan_id)
                    if plan_document:
                        plan_duration = plan_document.get('duration_days')

                if not expiration and plan_duration:
                    activation = user_data.get('planActivatedAt') or user_data.get('updatedAt') or user_data.get('createdAt')
                    if isinstance(activation, datetime):
                        expiration = activation + timedelta(days=plan_duration)

        return {
            'navbar_plan_expiration': expiration,
            'navbar_plan_duration': plan_duration,
            'now': now
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

    # Initialize database with default data if needed
    with app.app_context():
        from app.db_init import initialize_db
        initialize_db()

    return app
