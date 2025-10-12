from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import current_app

from app import mongo


class Click:
    """Click tracking model for client domains"""

    @staticmethod
    def track_click(
        client_id, domain_id, subdomain, ip_address=None, user_agent=None, referer=None
    ):
        """Track a click on a client's domain"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            click_data = {
                "client_id": client_id,
                "domain_id": domain_id,
                "subdomain": subdomain,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "referer": referer,
                "timestamp": datetime.utcnow(),
                "createdAt": datetime.utcnow(),
            }

            result = mongo.db.clicks.insert_one(click_data)

            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"

        except Exception as e:
            current_app.logger.error(f"Error tracking click: {e}")
            return False, str(e)

    @staticmethod
    def get_client_clicks(client_id, days=30):
        """Get all clicks for a client within specified days"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            clicks = list(
                mongo.db.clicks.find(
                    {"client_id": client_id, "timestamp": {"$gte": start_date, "$lte": end_date}}
                ).sort("timestamp", -1)
            )

            return clicks
        except Exception as e:
            current_app.logger.error(f"Error getting client clicks: {e}")
            return []

    @staticmethod
    def get_domain_clicks(client_id, domain_id, days=30):
        """Get clicks for a specific domain of a client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            clicks = list(
                mongo.db.clicks.find(
                    {
                        "client_id": client_id,
                        "domain_id": domain_id,
                        "timestamp": {"$gte": start_date, "$lte": end_date},
                    }
                ).sort("timestamp", -1)
            )

            return clicks
        except Exception as e:
            current_app.logger.error(f"Error getting domain clicks: {e}")
            return []

    @staticmethod
    def get_domain_click_count(client_id, domain_id, days=30):
        """Get count of clicks for a specific domain of a client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            count = mongo.db.clicks.count_documents(
                {
                    "client_id": client_id,
                    "domain_id": domain_id,
                    "timestamp": {"$gte": start_date, "$lte": end_date},
                }
            )

            return count
        except Exception as e:
            current_app.logger.error(f"Error getting domain click count: {e}")
            return 0

    @staticmethod
    def get_click_stats(client_id, days=30):
        """Get click statistics grouped by domain"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            pipeline = [
                {
                    "$match": {
                        "client_id": client_id,
                        "timestamp": {"$gte": start_date, "$lte": end_date},
                    }
                },
                {
                    "$group": {
                        "_id": {"domain_id": "$domain_id", "subdomain": "$subdomain"},
                        "total_clicks": {"$sum": 1},
                        "last_click": {"$max": "$timestamp"},
                        "unique_ips": {"$addToSet": "$ip_address"},
                    }
                },
                {
                    "$project": {
                        "domain_id": "$_id.domain_id",
                        "subdomain": "$_id.subdomain",
                        "total_clicks": 1,
                        "last_click": 1,
                        "unique_visitors": {"$size": "$unique_ips"},
                    }
                },
                {"$sort": {"total_clicks": -1}},
            ]

            stats = list(mongo.db.clicks.aggregate(pipeline))
            return stats
        except Exception as e:
            current_app.logger.error(f"Error getting click stats: {e}")
            return []

    @staticmethod
    def get_total_clicks(client_id, days=30):
        """Get total number of clicks for a client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            count = mongo.db.clicks.count_documents(
                {"client_id": client_id, "timestamp": {"$gte": start_date, "$lte": end_date}}
            )

            return count
        except Exception as e:
            current_app.logger.error(f"Error getting total clicks: {e}")
            return 0

    @staticmethod
    def get_clicks_by_date(client_id, days=30):
        """Get clicks grouped by date for charts"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            pipeline = [
                {
                    "$match": {
                        "client_id": client_id,
                        "timestamp": {"$gte": start_date, "$lte": end_date},
                    }
                },
                {
                    "$group": {
                        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "clicks": {"$sum": 1},
                    }
                },
                {"$sort": {"_id": 1}},
            ]

            result = list(mongo.db.clicks.aggregate(pipeline))
            return result
        except Exception as e:
            current_app.logger.error(f"Error getting clicks by date: {e}")
            return []
