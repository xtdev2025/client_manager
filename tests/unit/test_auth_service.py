"""
Unit tests for AuthService.
"""
from app.models.admin import Admin
from app.services.auth_service import AuthService


class TestAuthService:
    """Test cases for AuthService"""

    def test_validate_registration_data_success(self, app):
        """Test successful validation of registration data"""
        with app.app_context():
            valid, error = AuthService.validate_registration_data("testuser", "Admin@123")
            assert valid is True
            assert error is None

    def test_validate_registration_data_missing_username(self, app):
        """Test validation fails with missing username"""
        with app.app_context():
            valid, error = AuthService.validate_registration_data("", "Admin@123")
            assert valid is False
            assert "required" in error.lower()

    def test_validate_registration_data_missing_password(self, app):
        """Test validation fails with missing password"""
        with app.app_context():
            valid, error = AuthService.validate_registration_data("testuser", "")
            assert valid is False
            assert "required" in error.lower()

    def test_validate_registration_data_short_username(self, app):
        """Test validation fails with short username"""
        with app.app_context():
            valid, error = AuthService.validate_registration_data("ab", "Admin@123")
            assert valid is False
            assert "at least 3 characters" in error.lower()

    def test_validate_registration_data_short_password(self, app):
        """Test validation fails with short password"""
        with app.app_context():
            valid, error = AuthService.validate_registration_data("testuser", "12345")
            assert valid is False
            assert "at least 6 characters" in error.lower()

    def test_validate_registration_data_existing_username(self, app):
        """Test validation fails with existing username"""
        with app.app_context():
            # Create a user first
            Admin.create("existinguser", "Admin@123", "admin")

            # Try to validate with same username
            valid, error = AuthService.validate_registration_data("existinguser", "Admin@123")
            assert valid is False
            assert "already exists" in error.lower()

    def test_authenticate_user_success(self, app):
        """Test successful user authentication"""
        with app.app_context():
            # Create test admin
            Admin.create("superadmin", "Admin@123", "admin")

            # Authenticate
            success, user, error = AuthService.authenticate_user("superadmin", "Admin@123")
            assert success is True
            assert user is not None
            assert user["username"] == "superadmin"
            assert error is None

    def test_authenticate_user_invalid_password(self, app):
        """Test authentication fails with invalid password"""
        with app.app_context():
            # Create test admin
            Admin.create("superadmin", "Admin@123", "admin")

            # Try to authenticate with wrong password
            success, user, error = AuthService.authenticate_user("superadmin", "wrongpassword")
            assert success is False
            assert user is None
            assert error is not None

    def test_authenticate_user_nonexistent_user(self, app):
        """Test authentication fails with nonexistent user"""
        with app.app_context():
            success, user, error = AuthService.authenticate_user("nonexistent", "Admin@123")
            assert success is False
            assert user is None
            assert error is not None

    def test_authenticate_user_missing_credentials(self, app):
        """Test authentication fails with missing credentials"""
        with app.app_context():
            success, user, error = AuthService.authenticate_user("", "")
            assert success is False
            assert user is None
            assert "provide both" in error.lower()
