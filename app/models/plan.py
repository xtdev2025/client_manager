from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from bson.objectid import ObjectId
from flask import current_app

from app import mongo


class Plan:
    """Plan model for subscription plans"""

    @staticmethod
    def create(name: str, description: str, price: float, duration_days: int) -> Tuple[bool, str]:
        """
        Create a new plan.

        Args:
            name: The plan name
            description: The plan description
            price: The plan price
            duration_days: The plan duration in days

        Returns:
            Tuple containing success status and plan ID or error message
        """
        try:
            # Create plan object
            new_plan = {
                "name": name,
                "description": description,
                "price": float(price),
                "duration_days": int(duration_days),
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }

            # Insert into database
            result = mongo.db.plans.insert_one(new_plan)

            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"

        except Exception as e:
            current_app.logger.error(f"Error creating plan: {e}")
            return False, str(e)

    @staticmethod
    def update(plan_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update plan information.

        Args:
            plan_id: The plan ID
            data: Dict containing fields to update

        Returns:
            Tuple containing success status and message
        """
        try:
            if isinstance(plan_id, str):
                plan_id = ObjectId(plan_id)

            # Convert numeric fields
            if "price" in data:
                data["price"] = float(data["price"])
            if "duration_days" in data:
                data["duration_days"] = int(data["duration_days"])

            # Add updated timestamp
            data["updatedAt"] = datetime.utcnow()

            result = mongo.db.plans.update_one({"_id": plan_id}, {"$set": data})

            if result.modified_count > 0:
                return True, "Plan updated successfully"
            return False, "No changes made or plan not found"

        except Exception as e:
            current_app.logger.error(f"Error updating plan: {e}")
            return False, str(e)

    @staticmethod
    def delete(plan_id: str) -> Tuple[bool, str]:
        """
        Delete plan.

        Args:
            plan_id: The plan ID to delete

        Returns:
            Tuple containing success status and message
        """
        try:
            if isinstance(plan_id, str):
                plan_id = ObjectId(plan_id)

            # Check if plan is in use by any clients
            clients_with_plan = mongo.db.clients.count_documents({"plan_id": plan_id})
            if clients_with_plan > 0:
                return False, f"Cannot delete plan, it is being used by {clients_with_plan} clients"

            result = mongo.db.plans.delete_one({"_id": plan_id})

            if result.deleted_count > 0:
                return True, "Plan deleted successfully"
            return False, "Plan not found"

        except Exception as e:
            current_app.logger.error(f"Error deleting plan: {e}")
            return False, str(e)

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        Get all plans.

        Returns:
            List of plan dicts
        """
        try:
            plans = list(mongo.db.plans.find())
            return plans
        except Exception as e:
            current_app.logger.error(f"Error getting plans: {e}")
            return []

    @staticmethod
    def get_by_id(plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plan by ID.

        Args:
            plan_id: The plan ID

        Returns:
            Plan dict if found, None otherwise
        """
        try:
            if isinstance(plan_id, str):
                plan_id = ObjectId(plan_id)

            plan = mongo.db.plans.find_one({"_id": plan_id})
            return plan
        except Exception as e:
            current_app.logger.error(f"Error getting plan by ID: {e}")
            return None
