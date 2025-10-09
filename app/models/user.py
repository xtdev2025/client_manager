from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo, bcrypt

class User:
    """Base user class for both clients and admins"""
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
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
    def get_by_username(username):
        """Get user by username"""
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
    def check_password(user, password):
        """Check user password"""
        if 'password' in user:
            return bcrypt.check_password_hash(user['password'], password)
        return False