"""
Pytest configuration and fixtures for testing.
"""
import pytest
import os
from app import create_app, mongo


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017/client_manager_test'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    yield app


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth_headers():
    """Create authentication headers for testing"""
    return {
        'Content-Type': 'application/x-www-form-urlencoded'
    }


@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    """Clean database before each test"""
    with app.app_context():
        # Drop all test collections
        collections = ['users', 'admins', 'clients', 'plans', 'templates',
                      'domains', 'infos', 'login_logs', 'audit_logs',
                      'client_domains']
        for collection in collections:
            mongo.db[collection].delete_many({})
    
    yield
    
    # Cleanup after test
    with app.app_context():
        for collection in collections:
            mongo.db[collection].delete_many({})
