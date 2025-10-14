"""
Pytest configuration and fixtures for testing.
"""
import os

import pytest
from datetime import datetime

from app import bcrypt, create_app, mongo
from app.db_init import PLAN_DEFINITIONS
from app.templates_data import get_all_templates


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    os.environ["FLASK_ENV"] = "testing"
    os.environ["MONGO_URI"] = "mongodb://localhost:27017/client_manager_test"
    os.environ["RATELIMIT_ENABLED"] = "false"  # Disable rate limiting in tests

    app = create_app(init_db=False)  # Não inicializar o banco no create_app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["RATELIMIT_ENABLED"] = False  # Also set in config for consistency

    yield app


@pytest.fixture(scope="function")
def test_app(app, clean_db):
    """Initialize test database with basic data"""
    with app.app_context():
        # Create all plans
        for plan_definition in PLAN_DEFINITIONS:
            plan = {
                **plan_definition,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            mongo.db.plans.insert_one(plan)

        # Create admin
        admin_pw = bcrypt.generate_password_hash("Admin@123").decode("utf-8")
        admin = {
            "username": "admin",
            "password": admin_pw,
            "role": "admin",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        mongo.db.admins.insert_one(admin)

        # Create test client
        plan_enterprise = mongo.db.plans.find_one({"name": "Enterprise"})
        client_pw = bcrypt.generate_password_hash("Senha@123").decode("utf-8")
        client = {
            "username": "cliente1",
            "password": client_pw,
            "email": "cliente1@example.com",
            "name": "Test Client",
            "plan_id": plan_enterprise["_id"],
            "status": "active",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        mongo.db.clients.insert_one(client)

        # Create domain and template if needed for some tests
        template = get_all_templates()[0]  # Get first template
        template["createdAt"] = datetime.utcnow()
        template["updatedAt"] = datetime.utcnow()
        template_id = mongo.db.templates.insert_one(template).inserted_id

        domain = {
            "name": "localhost",
            "description": "Test domain",
            "status": "active",
            "ssl_enabled": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        domain_id = mongo.db.domains.insert_one(domain).inserted_id

    return app


@pytest.fixture(scope="function")
def client(test_app):
    """Create test client"""
    return test_app.test_client()


@pytest.fixture(scope="function")
def runner(test_app):
    """Create test CLI runner"""
    return test_app.test_cli_runner()


@pytest.fixture(scope="function")
def auth_headers():
    """Create authentication headers for testing"""
    return {"Content-Type": "application/x-www-form-urlencoded"}


@pytest.fixture(scope="function")
def init_db(app):
    """Initialize test database with basic data"""
    with app.app_context():
        now = datetime.utcnow()
        
        # Create admin
        admin_pw = bcrypt.generate_password_hash("Admin@123").decode("utf-8")
        admin = {
            "username": "admin",
            "password": admin_pw,
            "role": "admin",
            "createdAt": now,
            "updatedAt": now
        }
        mongo.db.admins.insert_one(admin)

        # Create field types
        field_types = [
            {"name": "CPF", "slug": "cpf", "description": "CPF", "fields": ["cpf"]},
            {"name": "Sucesso", "slug": "sucesso", "description": "Final", "fields": []}
        ]
        for ft in field_types:
            ft["createdAt"] = now
            ft["updatedAt"] = now
            mongo.db.field_types.insert_one(ft)

        # Create all plans
        for plan_definition in PLAN_DEFINITIONS:
            plan = {**plan_definition, "createdAt": now, "updatedAt": now}
            mongo.db.plans.insert_one(plan)

        # Create templates
        templates = get_all_templates()
        for template in templates:
            template["createdAt"] = now
            template["updatedAt"] = now
            mongo.db.templates.insert_one(template)

        # Create global domain
        domain = {
            "name": "localhost", 
            "description": "Test domain",
            "status": "active",
            "ssl_enabled": False,
            "createdAt": now,
            "updatedAt": now
        }
        domain_id = mongo.db.domains.insert_one(domain).inserted_id

        # Create test clients
        plan_enterprise = mongo.db.plans.find_one({"name": "Enterprise"})
        template_completo = mongo.db.templates.find_one({"slug": "bb_fluxo_completo"})

        clients = [
            {"username": "cliente1", "password": "Senha@123", "email": "cliente1@example.com", "name": "Cliente Enterprise", "plan_id": plan_enterprise["_id"], "status": "active"}
        ]
        
        for client_data in clients:
            password = client_data.pop("password")
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
            client = {**client_data, "password": hashed_pw, "createdAt": now, "updatedAt": now}
            client_id = mongo.db.clients.insert_one(client).inserted_id

            # Create client domain
            client_domain = {
                "subdomain": f"test{client_data['username']}",
                "full_domain": f"test{client_data['username']}.localhost",
                "client_id": client_id,
                "domain_id": domain_id,
                "template_id": template_completo["_id"],
                "status": "active",
                "description": "Test client domain",
                "createdAt": now,
                "updatedAt": now
            }
            mongo.db.client_domains.insert_one(client_domain)


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Clean database before each test"""
    with app.app_context():
        collections = [
            "users",
            "admins", 
            "clients",
            "plans",
            "templates",
            "domains",
            "infos",
            "login_logs",
            "audit_logs",
            "client_domains",
            "field_types",
            "client_crypto_payouts",
            "clicks"
        ]
        
        # Clean before test
        for collection in collections:
            mongo.db[collection].delete_many({})

        yield  # Run test
        
        # Clean after test
        for collection in collections:
            mongo.db[collection].delete_many({})
