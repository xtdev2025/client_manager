"""
Authentication service for handling authentication business logic.
"""
from typing import Optional, Tuple, Dict, Any
from flask import request
from app.models.user import User
from app.models.login_log import LoginLog


class AuthService:
    """Service class for authentication operations"""

    @staticmethod
    def authenticate_user(
        username: str, password: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with username and password.

        Args:
            username: The username to authenticate
            password: The password to verify

        Returns:
            Tuple containing:
                - success: bool indicating if authentication succeeded
                - user: dict with user data if successful, None otherwise
                - error_message: str with error message if failed, None otherwise
        """
        if not username or not password:
            return False, None, "Please provide both username and password"

        user = User.get_by_username(username)

        if not user:
            return False, None, "Invalid username or password"

        if not User.check_password(user, password):
            return False, None, "Invalid username or password"

        # Check if client account is active
        user_type = user.get('user_type', 'client')
        if user_type == 'client' and user.get('status') != 'active':
            return False, None, "Your account is not active. Please contact support."

        return True, user, None

    @staticmethod
    def log_login_attempt(
        user_id: str, username: str, success: bool,
        ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> bool:
        """
        Log a login attempt.

        Args:
            user_id: The user ID
            username: The username
            success: Whether the login was successful
            ip_address: The IP address of the client
            user_agent: The user agent string

        Returns:
            bool indicating if logging succeeded
        """
        if ip_address is None:
            ip_address = request.remote_addr
        if user_agent is None:
            user_agent = request.headers.get('User-Agent', 'Unknown')

        log_success, _ = LoginLog.create(
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )

        return log_success

    @staticmethod
    def validate_registration_data(
        username: str, password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate registration data.

        Args:
            username: The username to validate
            password: The password to validate

        Returns:
            Tuple containing:
                - valid: bool indicating if data is valid
                - error_message: str with error message if invalid, None otherwise
        """
        if not username or not password:
            return False, "Username and password are required"

        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(password) < 6:
            return False, "Password must be at least 6 characters long"

        if User.get_by_username(username):
            return False, "Username already exists"

        return True, None
