"""
Unit tests for ClientCryptoPayout model.
"""
from datetime import datetime, timedelta

import pytest
from bson.objectid import ObjectId

from app.models.client_crypto_payout import ClientCryptoPayout


class TestClientCryptoPayout:
    """Test cases for ClientCryptoPayout model"""

    @pytest.fixture
    def sample_client_id(self):
        """Generate a sample client ID"""
        return ObjectId()

    @pytest.fixture
    def sample_admin_id(self):
        """Generate a sample admin ID"""
        return ObjectId()

    def test_create_payout_success(self, app, sample_client_id, sample_admin_id):
        """Test successful payout creation"""
        with app.app_context():
            success, payout_id, error = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100.50,
                wallet_address="TRX123456789",
                idempotency_key="test-key-unique-001",
                origin=ClientCryptoPayout.ORIGIN_MANUAL,
                created_by=sample_admin_id,
            )

            assert success is True
            assert payout_id is not None
            assert error is None

            # Verify payout was created correctly
            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert payout is not None
            assert payout["client_id"] == sample_client_id
            assert payout["asset"] == "USDT"
            assert payout["network"] == "TRON"
            assert payout["amount"] == 100.50
            assert payout["wallet_address"] == "TRX123456789"
            assert payout["status"] == ClientCryptoPayout.STATUS_PENDING
            assert payout["origin"] == ClientCryptoPayout.ORIGIN_MANUAL
            assert payout["created_by"] == sample_admin_id
            assert payout["retryCount"] == 0
            assert payout["alertState"] == ClientCryptoPayout.ALERT_STATE_NONE
            assert payout["statusHistory"][0]["source"] == "creation"

    def test_create_payout_with_optional_fields(self, app, sample_client_id):
        """Test payout creation with optional fields"""
        with app.app_context():
            wallet_profile_id = ObjectId()
            trigger_metadata = {"plan_id": "plan123", "campaign": "activation_bonus"}

            success, payout_id, error = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="XRP",
                network="XRP",
                amount=50.0,
                wallet_address="XRP987654321",
                idempotency_key="test-key-unique-002",
                origin=ClientCryptoPayout.ORIGIN_BONUS,
                wallet_profile_id=wallet_profile_id,
                memo_tag="123456",
                trigger_metadata=trigger_metadata,
            )

            assert success is True

            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert payout["wallet_profile_id"] == wallet_profile_id
            assert payout["memo_tag"] == "123456"
            assert payout["trigger_metadata"] == trigger_metadata
            assert payout["origin"] == ClientCryptoPayout.ORIGIN_BONUS

    def test_create_payout_missing_required_fields(self, app, sample_client_id):
        """Test payout creation fails with missing fields"""
        with app.app_context():
            success, payout_id, error = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="key123",
            )

            assert success is False
            assert payout_id is None
            assert "Missing required fields" in error

    def test_create_payout_invalid_origin(self, app, sample_client_id):
        """Test payout creation fails with invalid origin"""
        with app.app_context():
            success, payout_id, error = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="key123",
                origin="invalid_origin",
            )

            assert success is False
            assert "Invalid origin" in error

    def test_create_payout_negative_amount(self, app, sample_client_id):
        """Test payout creation fails with negative amount"""
        with app.app_context():
            success, payout_id, error = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=-50,
                wallet_address="TRX123",
                idempotency_key="key123",
            )

            assert success is False
            assert "Amount must be greater than 0" in error

    def test_create_payout_duplicate_idempotency_key(self, app, sample_client_id):
        """Test payout creation fails with duplicate idempotency key"""
        with app.app_context():
            idempotency_key = "duplicate-key-001"

            # Create first payout
            success1, payout_id1, error1 = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key=idempotency_key,
            )
            assert success1 is True

            # Try to create second payout with same key
            success2, payout_id2, error2 = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key=idempotency_key,
            )

            assert success2 is False
            assert "already exists" in error2

    def test_get_by_id(self, app, sample_client_id):
        """Test getting payout by ID"""
        with app.app_context():
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-003",
            )

            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert payout is not None
            assert str(payout["_id"]) == payout_id

    def test_get_by_id_not_found(self, app):
        """Test getting non-existent payout"""
        with app.app_context():
            payout = ClientCryptoPayout.get_by_id(str(ObjectId()))
            assert payout is None

    def test_get_by_idempotency_key(self, app, sample_client_id):
        """Test getting payout by idempotency key"""
        with app.app_context():
            idempotency_key = "test-key-004"
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key=idempotency_key,
            )

            payout = ClientCryptoPayout.get_by_idempotency_key(idempotency_key)
            assert payout is not None
            assert payout["idempotency_key"] == idempotency_key

    def test_update_status(self, app, sample_client_id):
        """Test updating payout status"""
        with app.app_context():
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-005",
            )

            # Update to broadcast status
            success, error = ClientCryptoPayout.update_status(
                payout_id=payout_id,
                status=ClientCryptoPayout.STATUS_BROADCAST,
                heleket_transaction_id="heleket-tx-123",
            )

            assert success is True
            assert error is None

            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert payout["status"] == ClientCryptoPayout.STATUS_BROADCAST
            assert payout["heleket_transaction_id"] == "heleket-tx-123"

    def test_update_status_to_confirmed(self, app, sample_client_id):
        """Test updating status to confirmed sets confirmedAt"""
        with app.app_context():
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-006",
            )

            # Update to confirmed
            success, error = ClientCryptoPayout.update_status(
                payout_id=payout_id,
                status=ClientCryptoPayout.STATUS_CONFIRMED,
            )

            assert success is True

            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert payout["status"] == ClientCryptoPayout.STATUS_CONFIRMED
            assert payout["confirmedAt"] is not None

    def test_update_status_with_response_data(self, app, sample_client_id):
        """Test updating status with response data logging"""
        with app.app_context():
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-007",
            )

            response_data = {
                "transaction_id": "tx-123",
                "blockchain_hash": "0xabc123",
            }

            success, error = ClientCryptoPayout.update_status(
                payout_id=payout_id,
                status=ClientCryptoPayout.STATUS_BROADCAST,
                response_data=response_data,
            )

            assert success is True

            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert len(payout["responseLogs"]) == 1
            assert payout["responseLogs"][0]["data"] == response_data
            assert len(payout["statusHistory"]) >= 2

    def test_update_status_invalid_status(self, app, sample_client_id):
        """Test updating with invalid status fails"""
        with app.app_context():
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-008",
            )

            success, error = ClientCryptoPayout.update_status(
                payout_id=payout_id,
                status="invalid_status",
            )

            assert success is False
            assert "Invalid status" in error

    def test_update_heleket_payload(self, app, sample_client_id):
        """Test updating Heleket payload"""
        with app.app_context():
            success, payout_id, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-009",
            )

            payload = {
                "wallet_address": "TRX123",
                "amount": 100,
                "asset": "USDT",
                "network": "TRON",
            }

            success, error = ClientCryptoPayout.update_heleket_payload(
                payout_id=payout_id, payload=payload
            )

            assert success is True

            payout = ClientCryptoPayout.get_by_id(payout_id)
            assert payout["heleketPayload"] == payload

    def test_get_by_client(self, app, sample_client_id):
        """Test getting payouts by client"""
        with app.app_context():
            # Create multiple payouts for the client
            for i in range(3):
                ClientCryptoPayout.create(
                    client_id=sample_client_id,
                    asset="USDT",
                    network="TRON",
                    amount=100 + i,
                    wallet_address="TRX123",
                    idempotency_key=f"test-key-client-{i}",
                )

            # Create payout for different client
            other_client_id = ObjectId()
            ClientCryptoPayout.create(
                client_id=other_client_id,
                asset="USDT",
                network="TRON",
                amount=200,
                wallet_address="TRX456",
                idempotency_key="test-key-other",
            )

            payouts = ClientCryptoPayout.get_by_client(str(sample_client_id))
            assert len(payouts) == 3

    def test_get_by_client_with_status_filter(self, app, sample_client_id):
        """Test getting payouts by client with status filter"""
        with app.app_context():
            # Create pending payout
            success, payout_id1, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-pending",
            )

            # Create confirmed payout
            success, payout_id2, _ = ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=200,
                wallet_address="TRX123",
                idempotency_key="test-key-confirmed",
            )
            ClientCryptoPayout.update_status(
                payout_id2, ClientCryptoPayout.STATUS_CONFIRMED
            )

            # Get only confirmed payouts
            confirmed_payouts = ClientCryptoPayout.get_by_client(
                str(sample_client_id), status=ClientCryptoPayout.STATUS_CONFIRMED
            )
            assert len(confirmed_payouts) == 1
            assert confirmed_payouts[0]["status"] == ClientCryptoPayout.STATUS_CONFIRMED

    def test_get_by_status(self, app, sample_client_id):
        """Test getting payouts by status"""
        with app.app_context():
            # Create payouts with different statuses
            for i in range(2):
                success, payout_id, _ = ClientCryptoPayout.create(
                    client_id=sample_client_id,
                    asset="USDT",
                    network="TRON",
                    amount=100,
                    wallet_address="TRX123",
                    idempotency_key=f"test-key-status-{i}",
                )
                ClientCryptoPayout.update_status(
                    payout_id, ClientCryptoPayout.STATUS_CONFIRMED
                )

            # Create pending payout
            ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=100,
                wallet_address="TRX123",
                idempotency_key="test-key-status-pending",
            )

            confirmed_payouts = ClientCryptoPayout.get_by_status(
                ClientCryptoPayout.STATUS_CONFIRMED
            )
            assert len(confirmed_payouts) == 2

    def test_get_statistics(self, app, sample_client_id):
        """Test getting payout statistics"""
        with app.app_context():
            # Create payouts with different statuses
            for i in range(2):
                success, payout_id, _ = ClientCryptoPayout.create(
                    client_id=sample_client_id,
                    asset="USDT",
                    network="TRON",
                    amount=100,
                    wallet_address="TRX123",
                    idempotency_key=f"test-key-stats-confirmed-{i}",
                )
                ClientCryptoPayout.update_status(
                    payout_id, ClientCryptoPayout.STATUS_CONFIRMED
                )

            # Create pending payout
            ClientCryptoPayout.create(
                client_id=sample_client_id,
                asset="USDT",
                network="TRON",
                amount=50,
                wallet_address="TRX123",
                idempotency_key="test-key-stats-pending",
            )

            stats = ClientCryptoPayout.get_statistics()
            assert stats["total_count"] == 3
            assert stats["total_amount"] == 250
            assert ClientCryptoPayout.STATUS_CONFIRMED in stats["by_status"]
            assert stats["by_status"][ClientCryptoPayout.STATUS_CONFIRMED]["count"] == 2
            assert stats["by_status"][ClientCryptoPayout.STATUS_PENDING]["count"] == 1
