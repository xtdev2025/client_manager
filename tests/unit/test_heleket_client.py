"""
Unit tests for HeleketClient service.
"""
import hashlib
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.heleket_client import (
    HeleketAuthenticationError,
    HeleketClient,
    HeleketError,
)


class TestHeleketClient:
    """Test cases for HeleketClient"""

    @pytest.fixture
    def mock_config(self):
        """Mock app config with Heleket credentials"""
        return {
            "HELEKET_PROJECT_URL": "https://api.heleket.test",
            "HELEKET_MERCHANT_ID": "test-merchant-123",
            "HELEKET_API_KEY": "test-api-key-456",
        }

    @pytest.fixture
    def client(self, app, mock_config):
        """Create HeleketClient instance with mocked config"""
        with app.app_context():
            with patch.object(app.config, "get", side_effect=mock_config.get):
                return HeleketClient()

    def test_init_with_credentials(self, app):
        """Test client initialization with explicit credentials"""
        with app.app_context():
            client = HeleketClient(
                project_url="https://test.com",
                merchant_id="merchant123",
                api_key="key123",
            )
            assert client.project_url == "https://test.com"
            assert client.merchant_id == "merchant123"
            assert client.api_key == "key123"
            assert client.timeout == 30
            assert client.max_retries == 3

    def test_init_without_credentials_raises_error(self, app):
        """Test client initialization fails without credentials"""
        with app.app_context():
            with patch.object(app.config, "get", return_value=None):
                with pytest.raises(HeleketAuthenticationError):
                    HeleketClient()

    def test_get_headers(self, client):
        """Test header generation"""
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Merchant-ID"] == "test-merchant-123"
        assert headers["X-API-Key"] == "test-api-key-456"
        assert "X-Idempotency-Key" not in headers

    def test_get_headers_with_idempotency_key(self, client):
        """Test header generation with idempotency key"""
        headers = client._get_headers(idempotency_key="test-key-123")
        assert headers["X-Idempotency-Key"] == "test-key-123"

    def test_generate_idempotency_key(self):
        """Test idempotency key generation"""
        key = HeleketClient.generate_idempotency_key(
            client_id="client123", asset="USDT", timestamp="2025-10-14T12:00:00"
        )
        # Should be deterministic
        expected = hashlib.sha256("client123:USDT:2025-10-14T12:00:00".encode()).hexdigest()
        assert key == expected

    def test_generate_idempotency_key_without_timestamp(self):
        """Test idempotency key generation with auto timestamp"""
        key = HeleketClient.generate_idempotency_key(
            client_id="client123", asset="USDT"
        )
        assert isinstance(key, str)
        assert len(key) == 64  # SHA256 hex digest length

    @patch("app.services.heleket_client.requests.request")
    def test_create_payout_success(self, mock_request, client, app):
        """Test successful payout creation"""
        with app.app_context():
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "transaction_id": "tx-123",
                "status": "pending",
            }
            mock_request.return_value = mock_response

            success, data, error = client.create_payout(
                wallet_address="TRX123456789",
                asset="USDT",
                network="TRON",
                amount=100.50,
                idempotency_key="test-key-123",
            )

            assert success is True
            assert data["transaction_id"] == "tx-123"
            assert error is None

            # Verify request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "POST"
            assert "payouts" in call_args[1]["url"]
            assert call_args[1]["json"]["wallet_address"] == "TRX123456789"
            assert call_args[1]["json"]["amount"] == 100.50

    @patch("app.services.heleket_client.requests.request")
    def test_create_payout_with_memo_tag(self, mock_request, client, app):
        """Test payout creation with memo tag"""
        with app.app_context():
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"transaction_id": "tx-456"}
            mock_request.return_value = mock_response

            success, data, error = client.create_payout(
                wallet_address="XRP123456789",
                asset="XRP",
                network="XRP",
                amount=50.0,
                idempotency_key="test-key-456",
                memo_tag="123456",
            )

            assert success is True
            call_args = mock_request.call_args
            assert call_args[1]["json"]["memo_tag"] == "123456"

    def test_create_payout_validation_missing_fields(self, client):
        """Test payout creation fails with missing fields"""
        success, data, error = client.create_payout(
            wallet_address="",
            asset="USDT",
            network="TRON",
            amount=100,
            idempotency_key="key123",
        )

        assert success is False
        assert data is None
        assert "Missing required fields" in error

    def test_create_payout_validation_negative_amount(self, client):
        """Test payout creation fails with negative amount"""
        success, data, error = client.create_payout(
            wallet_address="TRX123",
            asset="USDT",
            network="TRON",
            amount=-50,
            idempotency_key="key123",
        )

        assert success is False
        assert "Amount must be greater than 0" in error

    @patch("app.services.heleket_client.requests.request")
    def test_create_payout_client_error(self, mock_request, client, app):
        """Test payout creation with client error (4xx)"""
        with app.app_context():
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Invalid wallet address"
            mock_response.headers = {"Content-Type": "text/plain"}
            mock_response.reason = "Bad Request"
            mock_request.return_value = mock_response

            success, data, error = client.create_payout(
                wallet_address="invalid",
                asset="USDT",
                network="TRON",
                amount=100,
                idempotency_key="key123",
            )

            assert success is False
            assert data is None
            assert "Client error 400" in error
            # Should not retry on client errors
            assert mock_request.call_count == 1

    @patch("app.services.heleket_client.requests.request")
    def test_create_payout_client_error_html(self, mock_request, client, app):
        """Test payout creation with HTML error response is sanitized."""
        with app.app_context():
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "<html><title>404 Not Found</title><body>Not Found</body></html>"
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.reason = "Not Found"
            mock_request.return_value = mock_response

            success, data, error = client.create_payout(
                wallet_address="invalid",
                asset="USDT",
                network="TRON",
                amount=100,
                idempotency_key="key123",
            )

            assert success is False
            assert data is None
            assert error == "Client error 404: Not Found"
            assert mock_request.call_count == 1

    @patch("app.services.heleket_client.requests.request")
    @patch("app.services.heleket_client.time.sleep")
    def test_create_payout_retry_on_server_error(self, mock_sleep, mock_request, client, app):
        """Test payout creation retries on server error (5xx)"""
        with app.app_context():
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.text = "Service unavailable"
            mock_request.return_value = mock_response

            success, data, error = client.create_payout(
                wallet_address="TRX123",
                asset="USDT",
                network="TRON",
                amount=100,
                idempotency_key="key123",
            )

            assert success is False
            assert data is None
            assert "Request failed after" in error
            # Should retry max_retries times
            assert mock_request.call_count == 3
            # Should use exponential backoff
            assert mock_sleep.call_count == 2

    @patch("app.services.heleket_client.requests.request")
    def test_get_payout_status_success(self, mock_request, client, app):
        """Test getting payout status"""
        with app.app_context():
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "transaction_id": "tx-123",
                "status": "confirmed",
            }
            mock_request.return_value = mock_response

            success, data, error = client.get_payout_status("tx-123")

            assert success is True
            assert data["status"] == "confirmed"
            assert error is None

    def test_get_payout_status_missing_id(self, client):
        """Test getting payout status without transaction ID"""
        success, data, error = client.get_payout_status("")

        assert success is False
        assert data is None
        assert "Transaction ID is required" in error

    @patch("app.services.heleket_client.requests.request")
    def test_cancel_payout_success(self, mock_request, client, app):
        """Test canceling a payout"""
        with app.app_context():
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "transaction_id": "tx-123",
                "status": "cancelled",
            }
            mock_request.return_value = mock_response

            success, data, error = client.cancel_payout("tx-123")

            assert success is True
            assert data["status"] == "cancelled"
            assert error is None

    def test_verify_webhook_signature(self, client, app):
        """Test webhook signature verification (placeholder)"""
        with app.app_context():
            payload = {"transaction_id": "tx-123"}
            signature = "test-signature"

            # Currently returns True as placeholder
            result = client.verify_webhook_signature(payload, signature)
            assert result is True
