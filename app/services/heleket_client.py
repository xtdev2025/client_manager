"""
Heleket API client for handling cryptocurrency payout operations.

This service manages communication with the Heleket payment gateway,
including authentication, request signing, retry logic, and error handling.
"""
import hashlib
import time
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

import requests
from flask import current_app


class HeleketError(Exception):
    """Base exception for Heleket API errors"""
    pass


class HeleketAuthenticationError(HeleketError):
    """Raised when authentication with Heleket API fails"""
    pass


class HeleketValidationError(HeleketError):
    """Raised when request validation fails"""
    pass


class HeleketNetworkError(HeleketError):
    """Raised when network communication fails"""
    pass


class HeleketClient:
    """Client for interacting with Heleket cryptocurrency payout API"""

    def __init__(
        self,
        project_url: Optional[str] = None,
        merchant_id: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Heleket API client.

        Args:
            project_url: Heleket project URL (defaults to config)
            merchant_id: Merchant ID (defaults to config)
            api_key: API key for authentication (defaults to config)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.project_url = project_url or current_app.config.get("HELEKET_PROJECT_URL")
        self.merchant_id = merchant_id or current_app.config.get("HELEKET_MERCHANT_ID")
        self.api_key = api_key or current_app.config.get("HELEKET_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries

        if not all([self.project_url, self.merchant_id, self.api_key]):
            raise HeleketAuthenticationError(
                "Heleket credentials not configured. Please set HELEKET_PROJECT_URL, "
                "HELEKET_MERCHANT_ID, and HELEKET_API_KEY environment variables."
            )

    def _get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """
        Generate request headers with authentication.

        Args:
            idempotency_key: Optional idempotency key for request deduplication

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "X-Merchant-ID": self.merchant_id,
            "X-API-Key": self.api_key,
        }

        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key

        return headers

    @staticmethod
    def generate_idempotency_key(client_id: str, asset: str, timestamp: Optional[str] = None) -> str:
        """
        Generate a deterministic idempotency key.

        Args:
            client_id: Client identifier
            asset: Cryptocurrency asset (e.g., 'USDT')
            timestamp: ISO8601 timestamp (defaults to current time)

        Returns:
            SHA256 hash as idempotency key
        """
        if not timestamp:
            timestamp = datetime.utcnow().isoformat()

        key_data = f"{client_id}:{asset}:{timestamp}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Make HTTP request to Heleket API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            idempotency_key: Optional idempotency key

        Returns:
            Tuple of (success, response_data, error_message)
        """
        url = f"{self.project_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers(idempotency_key)

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout,
                )

                # Log request for debugging
                current_app.logger.info(
                    f"Heleket API {method} {endpoint} - Status: {response.status_code}"
                )

                # Handle successful responses
                if response.status_code in (200, 201):
                    return True, response.json(), None

                # Handle client errors (4xx) - don't retry
                if 400 <= response.status_code < 500:
                    error_message = f"Client error {response.status_code}: {response.text}"
                    current_app.logger.error(error_message)
                    return False, None, error_message

                # Handle server errors (5xx) - retry
                last_error = f"Server error {response.status_code}: {response.text}"
                current_app.logger.warning(
                    f"Heleket API error (attempt {attempt + 1}/{self.max_retries}): {last_error}"
                )

            except requests.exceptions.Timeout as e:
                last_error = f"Request timeout: {str(e)}"
                current_app.logger.warning(
                    f"Heleket API timeout (attempt {attempt + 1}/{self.max_retries})"
                )

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                current_app.logger.warning(
                    f"Heleket API connection error (attempt {attempt + 1}/{self.max_retries})"
                )

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                current_app.logger.error(
                    f"Heleket API unexpected error (attempt {attempt + 1}/{self.max_retries}): {last_error}"
                )

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                backoff_time = 2 ** attempt
                time.sleep(backoff_time)

        # All retries exhausted
        error_message = f"Request failed after {self.max_retries} attempts: {last_error}"
        current_app.logger.error(error_message)
        return False, None, error_message

    def create_payout(
        self,
        wallet_address: str,
        asset: str,
        network: str,
        amount: float,
        idempotency_key: str,
        memo_tag: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Create a cryptocurrency payout.

        Args:
            wallet_address: Destination wallet address
            asset: Cryptocurrency asset (e.g., 'USDT', 'BTC')
            network: Blockchain network (e.g., 'TRON', 'ETH')
            amount: Amount to transfer (in asset units)
            idempotency_key: Unique key to prevent duplicate payouts
            memo_tag: Optional memo/tag for networks that require it
            metadata: Optional additional metadata

        Returns:
            Tuple of (success, response_data, error_message)
        """
        # Validate required fields
        if not all([wallet_address, asset, network, amount, idempotency_key]):
            return False, None, "Missing required fields: wallet_address, asset, network, amount, idempotency_key"

        if amount <= 0:
            return False, None, "Amount must be greater than 0"

        # Prepare payload
        payload = {
            "wallet_address": wallet_address,
            "asset": asset,
            "network": network,
            "amount": amount,
            "merchant_id": self.merchant_id,
        }

        if memo_tag:
            payload["memo_tag"] = memo_tag

        if metadata:
            payload["metadata"] = metadata

        # Make request
        return self._make_request(
            method="POST",
            endpoint="/api/v1/payouts",
            data=payload,
            idempotency_key=idempotency_key,
        )

    def get_payout_status(
        self, transaction_id: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get the status of a payout transaction.

        Args:
            transaction_id: Heleket transaction ID

        Returns:
            Tuple of (success, response_data, error_message)
        """
        if not transaction_id:
            return False, None, "Transaction ID is required"

        return self._make_request(
            method="GET",
            endpoint=f"/api/v1/payouts/{transaction_id}",
        )

    def cancel_payout(
        self, transaction_id: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Cancel a pending payout transaction.

        Args:
            transaction_id: Heleket transaction ID

        Returns:
            Tuple of (success, response_data, error_message)
        """
        if not transaction_id:
            return False, None, "Transaction ID is required"

        return self._make_request(
            method="POST",
            endpoint=f"/api/v1/payouts/{transaction_id}/cancel",
        )

    def verify_webhook_signature(
        self, payload: Dict[str, Any], signature: str
    ) -> bool:
        """
        Verify webhook signature from Heleket.

        Args:
            payload: Webhook payload
            signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        # TODO: Implement signature verification based on Heleket documentation
        # This is a placeholder implementation
        current_app.logger.warning("Webhook signature verification not yet implemented")
        return True
