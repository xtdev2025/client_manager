from datetime import datetime

from bson.objectid import ObjectId
from flask import current_app

from app import bcrypt, mongo
from app.models.user import User


class Admin(User):
    """Admin model for administrator management"""

    @staticmethod
    def create(username, password, role="admin"):
        """Create new admin"""
        try:
            # Check if username already exists
            if User.get_by_username(username):
                return False, "Username already exists"

            # Hash password
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

            # Create admin object
            new_admin = {
                "username": username,
                "password": hashed_pw,
                "role": role,  # 'admin' or 'super_admin'
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }

            # Insert into database
            result = mongo.db.admins.insert_one(new_admin)

            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"

        except Exception as e:
            current_app.logger.error(f"Error creating admin: {e}")
            return False, str(e)

    @staticmethod
    def update(admin_id, data):
        """Update admin information"""
        try:
            if isinstance(admin_id, str):
                admin_id = ObjectId(admin_id)

            # Ensure password is hashed if provided
            if "password" in data:
                data["password"] = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

            # Add updated timestamp
            data["updatedAt"] = datetime.utcnow()

            result = mongo.db.admins.update_one({"_id": admin_id}, {"$set": data})

            if result.modified_count > 0:
                return True, "Admin updated successfully"
            return False, "No changes made or admin not found"

        except Exception as e:
            current_app.logger.error(f"Error updating admin: {e}")
            return False, str(e)

    @staticmethod
    def delete(admin_id):
        """Delete admin"""
        try:
            if isinstance(admin_id, str):
                admin_id = ObjectId(admin_id)

            # Prevent deleting the last super_admin
            if Admin.is_last_super_admin(admin_id):
                return False, "Cannot delete the last super admin"

            result = mongo.db.admins.delete_one({"_id": admin_id})

            if result.deleted_count > 0:
                return True, "Admin deleted successfully"
            return False, "Admin not found"

        except Exception as e:
            current_app.logger.error(f"Error deleting admin: {e}")
            return False, str(e)

    @staticmethod
    def is_last_super_admin(admin_id):
        """Check if admin is the last super_admin"""
        try:
            if isinstance(admin_id, str):
                admin_id = ObjectId(admin_id)

            # Check if this admin is a super_admin
            admin = mongo.db.admins.find_one({"_id": admin_id})
            if not admin or admin.get("role") != "super_admin":
                return False

            # Count how many super_admins exist
            super_admin_count = mongo.db.admins.count_documents({"role": "super_admin"})
            return super_admin_count <= 1

        except Exception as e:
            current_app.logger.error(f"Error checking if last super admin: {e}")
            return True  # Safer to return True if there's an error

    @staticmethod
    def get_all():
        """Get all admins"""
        try:
            admins = list(mongo.db.admins.find())
            return admins
        except Exception as e:
            current_app.logger.error(f"Error getting admins: {e}")
            return []

    @staticmethod
    def get_by_id(admin_id):
        """Get admin by ID"""
        try:
            if isinstance(admin_id, str):
                admin_id = ObjectId(admin_id)

            admin = mongo.db.admins.find_one({"_id": admin_id})
            return admin
        except Exception as e:
            current_app.logger.error(f"Error getting admin by ID: {e}")
            return None
