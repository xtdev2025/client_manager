"""
Client crypto payout model for tracking Heleket payment requests.

This model manages cryptocurrency payout records sent to Heleket,
including transaction IDs, on-chain status, and audit metadata.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from bson.objectid import ObjectId
from flask import current_app

from app import mongo


class ClientCryptoPayout:
    """Model for client cryptocurrency payout records"""

    # Status constants
    STATUS_PENDING = "pending"
    STATUS_BROADCAST = "broadcast"
    STATUS_CONFIRMED = "confirmed"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    VALID_STATUSES = [
        STATUS_PENDING,
        STATUS_BROADCAST,
        STATUS_CONFIRMED,
        STATUS_FAILED,
        STATUS_CANCELLED,
    ]

    # Origin constants
    ORIGIN_MANUAL = "manual"
    ORIGIN_SCHEDULED = "scheduled"
    ORIGIN_BONUS = "bonus"

    VALID_ORIGINS = [ORIGIN_MANUAL, ORIGIN_SCHEDULED, ORIGIN_BONUS]

    @staticmethod
    def create(
        client_id: ObjectId,
        asset: str,
        network: str,
        amount: float,
        wallet_address: str,
        idempotency_key: str,
        origin: str = ORIGIN_MANUAL,
        wallet_profile_id: Optional[ObjectId] = None,
        memo_tag: Optional[str] = None,
        trigger_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[ObjectId] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new crypto payout record.

        Args:
            client_id: Client ObjectId
            asset: Cryptocurrency asset (e.g., 'USDT', 'BTC')
            network: Blockchain network (e.g., 'TRON', 'ETH')
            amount: Amount to transfer
            wallet_address: Destination wallet address
            idempotency_key: Unique key to prevent duplicates
            origin: Payout origin (manual, scheduled, bonus)
            wallet_profile_id: Optional wallet profile reference
            memo_tag: Optional memo/tag for certain networks
            trigger_metadata: Optional metadata about payout trigger
            created_by: Optional admin ID who created the payout

        Returns:
            Tuple of (success, payout_id, error_message)
        """
        try:
            # Validate required fields
            if not all([client_id, asset, network, amount, wallet_address, idempotency_key]):
                return False, None, "Missing required fields"

            if origin not in ClientCryptoPayout.VALID_ORIGINS:
                return False, None, f"Invalid origin. Must be one of: {ClientCryptoPayout.VALID_ORIGINS}"

            if amount <= 0:
                return False, None, "Amount must be greater than 0"

            # Check for duplicate idempotency_key
            existing = mongo.db.client_crypto_payouts.find_one(
                {"idempotency_key": idempotency_key}
            )
            if existing:
                return False, None, "Payout with this idempotency key already exists"

            # Convert to ObjectId if string
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if wallet_profile_id and isinstance(wallet_profile_id, str):
                wallet_profile_id = ObjectId(wallet_profile_id)
            if created_by and isinstance(created_by, str):
                created_by = ObjectId(created_by)

            # Prepare payout document
            now = datetime.utcnow()
            payout_data = {
                "client_id": client_id,
                "wallet_profile_id": wallet_profile_id,
                "heleket_transaction_id": None,  # Set when response received
                "status": ClientCryptoPayout.STATUS_PENDING,
                "asset": asset,
                "network": network,
                "amount": float(amount),
                "wallet_address": wallet_address,
                "memo_tag": memo_tag,
                "origin": origin,
                "trigger_metadata": trigger_metadata or {},
                "idempotency_key": idempotency_key,
                "requestedAt": now,
                "confirmedAt": None,
                "heleketPayload": None,  # Set when request is made
                "responseLogs": [],
                "created_by": created_by,
                "createdBy": created_by,  # manter compatibilidade com seeds antigos
                "createdAt": now,
                "updatedAt": now,
            }

            result = mongo.db.client_crypto_payouts.insert_one(payout_data)

            if result.inserted_id:
                current_app.logger.info(
                    f"Created crypto payout {result.inserted_id} for client {client_id}"
                )
                return True, str(result.inserted_id), None

            return False, None, "Failed to insert payout record"

        except Exception as e:
            error_msg = f"Error creating crypto payout: {str(e)}"
            current_app.logger.error(error_msg)
            return False, None, error_msg

    @staticmethod
    def get_by_id(payout_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a payout by its ID.

        Args:
            payout_id: Payout ID (string or ObjectId)

        Returns:
            Payout document or None if not found
        """
        try:
            if isinstance(payout_id, str):
                payout_id = ObjectId(payout_id)

            return mongo.db.client_crypto_payouts.find_one({"_id": payout_id})

        except Exception as e:
            current_app.logger.error(f"Error getting payout by ID: {e}")
            return None

    @staticmethod
    def get_by_idempotency_key(idempotency_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a payout by its idempotency key.

        Args:
            idempotency_key: Idempotency key

        Returns:
            Payout document or None if not found
        """
        try:
            return mongo.db.client_crypto_payouts.find_one(
                {"idempotency_key": idempotency_key}
            )

        except Exception as e:
            current_app.logger.error(f"Error getting payout by idempotency key: {e}")
            return None

    @staticmethod
    def get_by_transaction_id(heleket_transaction_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a payout by Heleket transaction identifier."""
        try:
            if not heleket_transaction_id:
                return None

            return mongo.db.client_crypto_payouts.find_one(
                {"heleket_transaction_id": heleket_transaction_id}
            )

        except Exception as e:
            current_app.logger.error(f"Error getting payout by Heleket transaction id: {e}")
            return None

    @staticmethod
    def update_status(
        payout_id: str,
        status: str,
        heleket_transaction_id: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Update payout status.

        Args:
            payout_id: Payout ID
            status: New status
            heleket_transaction_id: Optional Heleket transaction ID
            response_data: Optional response data to log

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if status not in ClientCryptoPayout.VALID_STATUSES:
                return False, f"Invalid status. Must be one of: {ClientCryptoPayout.VALID_STATUSES}"

            if isinstance(payout_id, str):
                payout_id = ObjectId(payout_id)

            set_data = {
                "status": status,
                "updatedAt": datetime.utcnow(),
            }

            if heleket_transaction_id:
                set_data["heleket_transaction_id"] = heleket_transaction_id

            if status == ClientCryptoPayout.STATUS_CONFIRMED:
                set_data["confirmedAt"] = datetime.utcnow()

            update_doc: Dict[str, Any] = {"$set": set_data}

            if response_data is not None:
                log_entry = {
                    "timestamp": datetime.utcnow(),
                    "status": status,
                    "data": response_data,
                }
                update_doc["$push"] = {"responseLogs": log_entry}

            result = mongo.db.client_crypto_payouts.update_one(
                {"_id": payout_id},
                update_doc
            )

            if result.modified_count > 0:
                current_app.logger.info(
                    f"Updated payout {payout_id} status to {status}"
                )
                return True, None

            return False, "Payout not found or no changes made"

        except Exception as e:
            error_msg = f"Error updating payout status: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def update_heleket_payload(
        payout_id: str, payload: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Store the Heleket API payload sent.

        Args:
            payout_id: Payout ID
            payload: Payload sent to Heleket

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if isinstance(payout_id, str):
                payout_id = ObjectId(payout_id)

            result = mongo.db.client_crypto_payouts.update_one(
                {"_id": payout_id},
                {
                    "$set": {
                        "heleketPayload": payload,
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0, None if result.modified_count > 0 else "Update failed"

        except Exception as e:
            error_msg = f"Error updating Heleket payload: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def get_by_client(
        client_id: str, status: Optional[str] = None, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get payouts for a specific client.

        Args:
            client_id: Client ID
            status: Optional status filter
            days: Number of days to look back

        Returns:
            List of payout documents
        """
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            query = {
                "client_id": client_id,
                "createdAt": {"$gte": start_date, "$lte": end_date},
            }

            if status:
                query["status"] = status

            payouts = list(
                mongo.db.client_crypto_payouts.find(query).sort("createdAt", -1)
            )

            return payouts

        except Exception as e:
            current_app.logger.error(f"Error getting client payouts: {e}")
            return []

    @staticmethod
    def get_by_status(
        status: str, days: int = 30, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get payouts by status.

        Args:
            status: Status to filter by
            days: Number of days to look back
            limit: Maximum number of results

        Returns:
            List of payout documents
        """
        try:
            if status not in ClientCryptoPayout.VALID_STATUSES:
                current_app.logger.error(f"Invalid status: {status}")
                return []

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            payouts = list(
                mongo.db.client_crypto_payouts.find(
                    {
                        "status": status,
                        "createdAt": {"$gte": start_date, "$lte": end_date},
                    }
                )
                .sort("createdAt", -1)
                .limit(limit)
            )

            return payouts

        except Exception as e:
            current_app.logger.error(f"Error getting payouts by status: {e}")
            return []

    @staticmethod
    def get_statistics(days: int = 30) -> Dict[str, Any]:
        """
        Get payout statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with statistics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            pipeline = [
                {"$match": {"createdAt": {"$gte": start_date, "$lte": end_date}}},
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                    }
                },
            ]

            stats_by_status = list(mongo.db.client_crypto_payouts.aggregate(pipeline))

            # Format results
            statistics = {
                "period_days": days,
                "by_status": {},
                "total_count": 0,
                "total_amount": 0,
            }

            for stat in stats_by_status:
                status = stat["_id"]
                statistics["by_status"][status] = {
                    "count": stat["count"],
                    "total_amount": stat["total_amount"],
                }
                statistics["total_count"] += stat["count"]
                statistics["total_amount"] += stat["total_amount"]

            return statistics

        except Exception as e:
            current_app.logger.error(f"Error getting payout statistics: {e}")
            return {
                "period_days": days,
                "by_status": {},
                "total_count": 0,
                "total_amount": 0,
            }

    @staticmethod
    def create_indexes():
        """
        Create database indexes for optimal query performance.

        This should be called during application initialization.
        """
        try:
            # Index on client_id and createdAt for client queries
            mongo.db.client_crypto_payouts.create_index(
                [("client_id", 1), ("createdAt", -1)]
            )

            # Index on status, requestedAt, and asset for admin queries
            mongo.db.client_crypto_payouts.create_index(
                [("status", 1), ("requestedAt", -1), ("asset", 1)]
            )

            # Unique index on idempotency_key to prevent duplicates
            mongo.db.client_crypto_payouts.create_index(
                "idempotency_key", unique=True
            )

            # Index on heleket_transaction_id for reconciliation
            mongo.db.client_crypto_payouts.create_index("heleket_transaction_id")

            current_app.logger.info("Created indexes for client_crypto_payouts collection")

        except Exception as e:
            current_app.logger.error(f"Error creating indexes: {e}")

    @staticmethod
    def mark_webhook_received(payout_id: str) -> None:
        """Annotate payout document with latest webhook timestamp."""
        try:
            if isinstance(payout_id, str):
                payout_id = ObjectId(payout_id)

            mongo.db.client_crypto_payouts.update_one(
                {"_id": payout_id},
                {
                    "$set": {
                        "lastWebhookAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow(),
                    }
                },
            )
        except Exception as e:
            current_app.logger.error(f"Error marking webhook reception: {e}")
