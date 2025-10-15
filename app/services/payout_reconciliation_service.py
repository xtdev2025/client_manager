"""Utilities for reconciling Heleket payout statuses."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import current_app

from app import mongo
from app.models.client_crypto_payout import ClientCryptoPayout
from app.services.audit_helper import log_change
from app.services.heleket_client import HeleketClient, HeleketError


class PayoutReconciliationService:
    """Coordinate status reconciliation for Heleket payouts."""

    DEFAULT_MIN_DELAY_MINUTES = 5
    DEFAULT_POLL_INTERVAL_MINUTES = 5
    DEFAULT_ALERT_ATTEMPTS = 3
    DEFAULT_ALERT_AGE_MINUTES = 30
    DEFAULT_LOOKBACK_DAYS = 7

    @staticmethod
    def schedule_pending(
        *,
        limit: int = 100,
        heleket_client: Optional[HeleketClient] = None,
        min_delay_minutes: Optional[int] = None,
        poll_interval_minutes: Optional[int] = None,
        alert_attempts: Optional[int] = None,
        alert_age_minutes: Optional[int] = None,
        lookback_days: Optional[int] = None,
    ) -> Dict[str, int]:
        """Poll payouts awaiting confirmation and update their status."""
        now = datetime.utcnow()

        min_delay = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_MIN_DELAY_MINUTES", min_delay_minutes, PayoutReconciliationService.DEFAULT_MIN_DELAY_MINUTES
        )
        poll_interval = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_INTERVAL_MINUTES", poll_interval_minutes, PayoutReconciliationService.DEFAULT_POLL_INTERVAL_MINUTES
        )
        alert_attempts = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_ALERT_ATTEMPTS", alert_attempts, PayoutReconciliationService.DEFAULT_ALERT_ATTEMPTS
        )
        alert_age_minutes = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_ALERT_AGE_MINUTES", alert_age_minutes, PayoutReconciliationService.DEFAULT_ALERT_AGE_MINUTES
        )
        lookback_days = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_LOOKBACK_DAYS", lookback_days, PayoutReconciliationService.DEFAULT_LOOKBACK_DAYS
        )

        lookback_threshold = now - timedelta(days=lookback_days)
        due_threshold = now - timedelta(minutes=min_delay)

        query = {
            "$and": [
                {"status": {"$in": list(ClientCryptoPayout.ACTIVE_STATUSES)}},
                {"requestedAt": {"$gte": lookback_threshold, "$lte": due_threshold}},
                {
                    "$or": [
                        {"nextStatusCheckAt": {"$exists": False}},
                        {"nextStatusCheckAt": None},
                        {"nextStatusCheckAt": {"$lte": now}},
                    ]
                },
            ]
        }

        cursor = mongo.db.client_crypto_payouts.find(query).sort("requestedAt", 1).limit(limit)

        results = {"checked": 0, "finalized": 0, "alerts": 0, "errors": 0}
        for document in cursor:
            success, outcome = PayoutReconciliationService.check_now(
                payout_doc=document,
                heleket_client=heleket_client,
                poll_interval_minutes=poll_interval,
                alert_attempts=alert_attempts,
                alert_age_minutes=alert_age_minutes,
            )

            if not success:
                results["errors"] += 1
                continue

            results["checked"] += 1
            if outcome.get("finalized"):
                results["finalized"] += 1
            if outcome.get("alert_triggered"):
                results["alerts"] += 1

        return results

    @staticmethod
    def check_now(
        *,
        payout_id: Optional[str] = None,
        payout_doc: Optional[Dict[str, Any]] = None,
        heleket_client: Optional[HeleketClient] = None,
        poll_interval_minutes: Optional[int] = None,
        alert_attempts: Optional[int] = None,
        alert_age_minutes: Optional[int] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Fetch latest status for a payout and persist changes."""
        try:
            document = payout_doc or PayoutReconciliationService._load_document(payout_id)
        except ValueError as exc:
            return False, {"error": str(exc)}

        if document is None:
            return False, {"error": "payout_not_found"}

        payout_id = str(document.get("_id"))
        transaction_id = document.get("heleket_transaction_id")
        poll_interval = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_INTERVAL_MINUTES",
            poll_interval_minutes,
            PayoutReconciliationService.DEFAULT_POLL_INTERVAL_MINUTES,
        )
        alert_attempts = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_ALERT_ATTEMPTS",
            alert_attempts,
            PayoutReconciliationService.DEFAULT_ALERT_ATTEMPTS,
        )
        alert_age_minutes = PayoutReconciliationService._config_value(
            "PAYOUT_RECON_ALERT_AGE_MINUTES",
            alert_age_minutes,
            PayoutReconciliationService.DEFAULT_ALERT_AGE_MINUTES,
        )

        now = datetime.utcnow()
        next_check_at = now + timedelta(minutes=poll_interval)
        retry_count = int(document.get("retryCount", 0) or 0)

        outcome: Dict[str, Any] = {
            "payout_id": payout_id,
            "previous_status": document.get("status"),
            "finalized": False,
            "alert_triggered": False,
        }

        if not transaction_id:
            retry_count += 1
            extra_fields = {
                "lastStatusCheckAt": now,
                "lastStatusCheckSource": "polling",
                "nextStatusCheckAt": next_check_at,
                "retryCount": retry_count,
                "failureReason": "missing_transaction_id",
            }
            alert_updates, alert_triggered, _ = PayoutReconciliationService._compute_alert_updates(
                document, retry_count, now, alert_attempts, alert_age_minutes
            )
            extra_fields.update(alert_updates)

            ClientCryptoPayout.update_status(
                payout_id=payout_id,
                status=document.get("status", ClientCryptoPayout.STATUS_PENDING),
                status_source="polling",
                status_details={"error": "missing_transaction_id"},
                extra_fields=extra_fields,
                append_history=False,
            )

            outcome["alert_triggered"] = alert_triggered
            outcome["error"] = "missing_transaction_id"
            return False, outcome

        heleket_client = heleket_client or HeleketClient()

        try:
            api_success, api_response, api_error = heleket_client.get_payout_status(transaction_id)
        except HeleketError as exc:
            api_success, api_response, api_error = False, None, str(exc)

        if not api_success:
            retry_count += 1
            extra_fields = {
                "lastStatusCheckAt": now,
                "lastStatusCheckSource": "polling",
                "nextStatusCheckAt": next_check_at,
                "retryCount": retry_count,
                "failureReason": api_error,
            }
            alert_updates, alert_triggered, alert_reasons = PayoutReconciliationService._compute_alert_updates(
                document, retry_count, now, alert_attempts, alert_age_minutes
            )
            extra_fields.update(alert_updates)

            ClientCryptoPayout.update_status(
                payout_id=payout_id,
                status=document.get("status", ClientCryptoPayout.STATUS_PENDING),
                response_data={"source": "polling", "error": api_error},
                status_source="polling",
                status_details={"errors": alert_reasons or [api_error] if api_error else alert_reasons},
                extra_fields=extra_fields,
                append_history=False,
            )

            PayoutReconciliationService._log_audit(
                action="reconcile_error",
                payout_id=payout_id,
                details={
                    "transaction_id": transaction_id,
                    "error": api_error,
                    "retry_count": retry_count,
                    "alert_triggered": alert_triggered,
                    "alert_reasons": alert_reasons,
                },
            )

            outcome["alert_triggered"] = alert_triggered
            outcome["error"] = api_error
            return False, outcome

        normalized_status = ClientCryptoPayout.normalize_status(
            (api_response or {}).get("status") if api_response else None
        ) or document.get("status", ClientCryptoPayout.STATUS_PENDING)

        is_final = normalized_status in ClientCryptoPayout.FINAL_STATUSES
        retry_count = 0 if is_final else retry_count

        extra_fields = {
            "lastStatusCheckAt": now,
            "lastStatusCheckSource": "polling",
            "nextStatusCheckAt": None if is_final else next_check_at,
            "retryCount": retry_count,
            "failureReason": None,
        }

        alert_updates, alert_triggered, alert_reasons = PayoutReconciliationService._compute_alert_updates(
            document, retry_count, now, alert_attempts, alert_age_minutes
        )
        if is_final and alert_updates.get("alertState") == ClientCryptoPayout.ALERT_STATE_PENDING_REVIEW:
            alert_updates = {
                **alert_updates,
                "alertState": ClientCryptoPayout.ALERT_STATE_NONE,
                "alertEmittedAt": None,
            }
            alert_triggered = False
        extra_fields.update(alert_updates)

        ClientCryptoPayout.update_status(
            payout_id=payout_id,
            status=normalized_status,
            heleket_transaction_id=transaction_id,
            response_data={"source": "polling", "payload": api_response},
            status_source="polling",
            status_details={
                "raw_status": (api_response or {}).get("status"),
                "final": is_final,
            },
            extra_fields=extra_fields,
            append_history=True,
        )

        PayoutReconciliationService._log_audit(
            action="reconcile_success",
            payout_id=payout_id,
            details={
                "transaction_id": transaction_id,
                "status": normalized_status,
                "finalized": is_final,
                "alert_triggered": alert_triggered,
                "alert_reasons": alert_reasons,
            },
        )

        outcome["status"] = normalized_status
        outcome["finalized"] = is_final
        outcome["alert_triggered"] = alert_triggered
        return True, outcome

    @staticmethod
    def _load_document(payout_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if not payout_id:
            raise ValueError("payout_id is required when payout_doc is not provided")

        if isinstance(payout_id, str):
            try:
                payout_id_obj = ObjectId(payout_id)
            except (InvalidId, TypeError) as exc:
                raise ValueError(f"invalid payout_id: {payout_id}") from exc
        elif isinstance(payout_id, ObjectId):
            payout_id_obj = payout_id
        else:
            raise ValueError("payout_id must be a string or ObjectId")

        return mongo.db.client_crypto_payouts.find_one({"_id": payout_id_obj})

    @staticmethod
    def _compute_alert_updates(
        document: Dict[str, Any],
        retry_count: int,
        now: datetime,
        alert_attempts: int,
        alert_age_minutes: int,
    ) -> Tuple[Dict[str, Any], bool, List[str]]:
        current_state = document.get("alertState", ClientCryptoPayout.ALERT_STATE_NONE)
        requested_at = document.get("requestedAt")
        reasons: List[str] = []

        if alert_attempts and retry_count >= alert_attempts:
            reasons.append("retries")

        if alert_age_minutes and isinstance(requested_at, datetime):
            if requested_at <= now - timedelta(minutes=alert_age_minutes):
                reasons.append("age")

        updates: Dict[str, Any] = {}
        triggered = False

        if reasons:
            if current_state != ClientCryptoPayout.ALERT_STATE_PENDING_REVIEW:
                updates["alertState"] = ClientCryptoPayout.ALERT_STATE_PENDING_REVIEW
                updates["alertEmittedAt"] = now
                triggered = True
        elif current_state == ClientCryptoPayout.ALERT_STATE_PENDING_REVIEW:
            updates["alertState"] = ClientCryptoPayout.ALERT_STATE_NONE
            updates["alertEmittedAt"] = None

        return updates, triggered, reasons

    @staticmethod
    def _config_value(config_key: str, override: Optional[int], default: int) -> int:
        if override is not None:
            return override
        try:
            value = current_app.config.get(config_key)
            if value is None:
                return default
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _log_audit(action: str, payout_id: str, details: Dict[str, Any]) -> None:
        log_change(
            "payout",
            action,
            entity_id=payout_id,
            payload=details,
            actor_user_id="payout_reconciliation",
            ip_address="system",
        )
