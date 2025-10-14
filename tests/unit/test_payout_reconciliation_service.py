"""Unit tests for PayoutReconciliationService."""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import pytest
from bson.objectid import ObjectId

from app import mongo
from app.models.client_crypto_payout import ClientCryptoPayout
from app.services.payout_reconciliation_service import PayoutReconciliationService


class DummyStatusClient:
    """Dummy Heleket client to simulate status polling."""

    def __init__(
        self,
        *,
        should_succeed: bool = True,
        status: str = ClientCryptoPayout.STATUS_CONFIRMED,
        error: Optional[str] = None,
    ) -> None:
        self.should_succeed = should_succeed
        self.status = status
        self.error = error or "timeout"
        self.calls = []

    def get_payout_status(self, transaction_id: str) -> Tuple[bool, Optional[Dict[str, str]], Optional[str]]:
        self.calls.append(transaction_id)
        if self.should_succeed:
            return True, {"status": self.status, "transaction_id": transaction_id}, None
        return False, None, self.error


@pytest.fixture
def payout_id(app):
    """Create a sample payout ready for reconciliation."""
    with app.app_context():
        success, payout_id, _ = ClientCryptoPayout.create(
            client_id=ObjectId(),
            asset="USDT",
            network="TRON",
            amount=150.0,
            wallet_address="TRX123",
            idempotency_key="recon-test-001",
        )
        assert success is True

        mongo.db.client_crypto_payouts.update_one(
            {"_id": ObjectId(payout_id)},
            {
                "$set": {
                    "status": ClientCryptoPayout.STATUS_BROADCAST,
                    "heleket_transaction_id": "tx-recon-001",
                    "requestedAt": datetime.utcnow() - timedelta(minutes=20),
                    "nextStatusCheckAt": None,
                }
            },
        )

        yield payout_id


def test_check_now_updates_status_on_success(app, payout_id):
    dummy_client = DummyStatusClient(status="confirmed")

    with app.app_context():
        document = ClientCryptoPayout.get_by_id(payout_id)
        success, outcome = PayoutReconciliationService.check_now(
            payout_doc=document,
            heleket_client=dummy_client,
            poll_interval_minutes=10,
        )

        assert success is True
        assert outcome["status"] == ClientCryptoPayout.STATUS_CONFIRMED
        assert outcome["finalized"] is True
        assert dummy_client.calls == ["tx-recon-001"]

        updated = ClientCryptoPayout.get_by_id(payout_id)
        assert updated["status"] == ClientCryptoPayout.STATUS_CONFIRMED
        assert updated["retryCount"] == 0
        assert updated["nextStatusCheckAt"] is None
        assert updated["failureReason"] is None
        assert updated["statusHistory"][-1]["source"] == "polling"


def test_check_now_records_error_and_alert(app, payout_id):
    dummy_client = DummyStatusClient(should_succeed=False, error="gateway timeout")

    with app.app_context():
        document = ClientCryptoPayout.get_by_id(payout_id)
        success, outcome = PayoutReconciliationService.check_now(
            payout_doc=document,
            heleket_client=dummy_client,
            poll_interval_minutes=5,
            alert_attempts=1,
            alert_age_minutes=10,
        )

        assert success is False
        assert outcome["error"] == "gateway timeout"
        assert outcome["alert_triggered"] is True

        updated = ClientCryptoPayout.get_by_id(payout_id)
        assert updated["retryCount"] == 1
        assert updated["failureReason"] == "gateway timeout"
        assert updated["alertState"] == ClientCryptoPayout.ALERT_STATE_PENDING_REVIEW
        assert updated["nextStatusCheckAt"] is not None


def test_schedule_pending_processes_due_payout(app, payout_id):
    dummy_client = DummyStatusClient(status="broadcast")

    with app.app_context():
        results = PayoutReconciliationService.schedule_pending(
            limit=5,
            heleket_client=dummy_client,
            min_delay_minutes=5,
            poll_interval_minutes=5,
        )

        assert results["checked"] == 1
        assert results["errors"] == 0
        assert dummy_client.calls == ["tx-recon-001"]

        updated = ClientCryptoPayout.get_by_id(payout_id)
        assert updated["lastStatusCheckSource"] == "polling"
        assert updated["retryCount"] >= 0
