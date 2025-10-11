from typing import Optional, Dict, Any
from flask import current_app
from bson.objectid import ObjectId
from app import mongo, bcrypt


class User:
    """Base user class for both clients and admins"""

    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: The user ID as string or ObjectId

        Returns:
            User dict if found, None otherwise
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            # Check in both collections
            user = mongo.db.clients.find_one({'_id': user_id})
            if not user:
                user = mongo.db.admins.find_one({'_id': user_id})

            if user:
                # Add user type
                if 'role' not in user:
                    if mongo.db.clients.find_one({'_id': user_id}):
                        user['user_type'] = 'client'
                    else:
                        user['user_type'] = 'admin'
                return user
        except Exception as e:
            current_app.logger.error(f"Error getting user by ID: {e}")
        return None

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.

        Args:
            username: The username to search for

        Returns:
            User dict if found, None otherwise
        """
        try:
            # Check in both collections
            user = mongo.db.clients.find_one({'username': username})
            if not user:
                user = mongo.db.admins.find_one({'username': username})

            if user:
                # Add user type
                if mongo.db.clients.find_one({'username': username}):
                    user['user_type'] = 'client'
                else:
                    user['user_type'] = 'admin'
                return user
        except Exception as e:
            current_app.logger.error(f"Error getting user by username: {e}")
        return None

    @staticmethod
    def check_password(user: Dict[str, Any], password: str) -> bool:
        """
        Check user password.

        Args:
            user: The user dict containing password hash
            password: The plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        if 'password' in user:
            return bcrypt.check_password_hash(user['password'], password)
        return False
