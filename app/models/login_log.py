from datetime import datetime

from bson.objectid import ObjectId
from flask import current_app

from app import mongo


class LoginLog:
    """Model helper for recording and retrieving user login events."""

    @staticmethod
    def collection():
        db = getattr(mongo, "db", None)
        if db is None:
            raise RuntimeError("Mongo database is not configured")
        return db.login_logs

    @staticmethod
    def record(user_id, username, role, user_type, ip_address=None, user_agent=None):
        """Persist a login event for auditing purposes."""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            doc = {
                "user_id": user_id,
                "username": username,
                "role": role,
                "user_type": user_type,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow(),
            }

            result = LoginLog.collection().insert_one(doc)
            return bool(result.inserted_id)
        except Exception as exc:
            current_app.logger.error(f"Failed to record login event: {exc}")
            return False

    @staticmethod
    def get_recent(limit=15):
        """Return the most recent login events ordered by newest first."""
        try:
            cursor = LoginLog.collection().find().sort("created_at", -1).limit(limit)
            return list(cursor)
        except Exception as exc:
            current_app.logger.error(f"Failed to fetch login events: {exc}")
            return []

    @staticmethod
    def clear_for_user(user_id):
        """Utility to delete login logs for a specific user (not exposed in UI)."""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            LoginLog.collection().delete_many({"user_id": user_id})
        except Exception as exc:
            current_app.logger.warning(f"Failed to clear login events for user {user_id}: {exc}")
