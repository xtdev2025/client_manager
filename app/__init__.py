from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import config
import os

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

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
    
    # Initialize user loader
    from app.utils.user_loader import init_user_loader
    init_user_loader(login_manager)

    # Register blueprints
    from app.controllers.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.controllers.client import client as client_blueprint
    app.register_blueprint(client_blueprint)
    
    from app.controllers.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    from app.controllers.plan import plan as plan_blueprint
    app.register_blueprint(plan_blueprint)
    
    from app.controllers.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Initialize database with default data if needed
    with app.app_context():
        from app.db_init import initialize_db
        initialize_db()
    
    return app