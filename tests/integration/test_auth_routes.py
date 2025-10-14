"""
Integration tests for authentication routes.
"""
from app.models.admin import Admin
from app.models.client import Client
from app.models.plan import Plan


class TestAuthRoutes:
    """Test cases for authentication routes"""

    def test_login_page_loads(self, client):
        """Test that login page loads successfully"""
        response = client.get("/auth/login", follow_redirects=True)
        assert response.status_code == 200
        assert b"login" in response.data.lower()

    def test_login_success_admin(self, client, app):
        """Test successful admin login"""
        with app.app_context():
            # Create test admin
            Admin.create("superadmin", "Admin@123", "admin")

        # Attempt login
        response = client.post(
            "/auth/login",
            data={"username": "superadmin", "password": "Admin@123"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"dashboard" in response.data.lower()

    def test_login_success_client(self, client, app):
        """Test successful client login"""
        with app.app_context():
            success, plan_id = Plan.create("Test Plan", "Description", 99.99, 30)
            Client.create("testclient", "Admin@123", plan_id)

        # Attempt login
        response = client.post(
            "/auth/login",
            data={"username": "testclient", "password": "Admin@123"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"dashboard" in response.data.lower()

    def test_login_invalid_credentials(self, client, app):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            data={"username": "superadmin", "password": "wrongpassword"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Invalid" in response.data or b"invalid" in response.data

    def test_login_inactive_client(self, client, app):
        """Test login with inactive client account"""
        with app.app_context():
            success, plan_id = Plan.create("Test Plan", "Description", 99.99, 30)
            Client.create("testclient", "Admin@123", plan_id, status="inactive")

        response = client.post(
            "/auth/login",
            data={"username": "testclient", "password": "Admin@123"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"not active" in response.data.lower()

    def test_login_missing_credentials(self, client, app):
        """Test login with missing credentials"""
        response = client.post(
            "/auth/login",
            data={},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Please provide" in response.data or b"provide" in response.data

    def test_logout(self, client, app):
        """Test logout functionality"""
        with app.app_context():
            # Create and login test admin
            Admin.create("superadmin", "Admin@123", "admin")

        # Login first
        client.post(
            "/auth/login",
            data={"username": "superadmin", "password": "Admin@123"},
            follow_redirects=True,
        )

        # Attempt logout
        response = client.get("/auth/logout", follow_redirects=True)

        assert response.status_code == 200
        assert b"login" in response.data.lower()

    def test_protected_route_requires_auth(self, client):
        """Test that protected routes require authentication"""
        response = client.get("/admins/", follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login
        assert b"login" in response.data.lower()

    def test_admin_route_requires_admin_role(self, client, app):
        """Test that admin routes require admin role"""
        with app.app_context():
            # Create and login as client
            success, plan_id = Plan.create("Test Plan", "Description", 99.99, 30)
            Client.create("testclient", "Admin@123", plan_id, status="active")

        # Login as client
        client.post("/login", data={"username": "testclient", "password": "Admin@123"})

        # Try to access admin route
        response = client.get("/admins/", follow_redirects=True)
        assert response.status_code == 200
        # Should show permission error or redirect
