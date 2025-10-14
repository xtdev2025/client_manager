# Heleket API Client Documentation

## Overview

The Heleket API Client provides a robust interface for interacting with the Heleket cryptocurrency payout gateway. It handles authentication, request retry logic with exponential backoff, error handling, and idempotency management.

## Installation & Configuration

### Environment Variables

The following environment variables must be set:

```bash
HELEKET_PROJECT_URL=https://api.heleket.com  # Heleket API base URL
HELEKET_MERCHANT_ID=your-merchant-id         # Your Heleket merchant ID
HELEKET_API_KEY=your-api-key                 # Your Heleket API key
```

These should be configured in:
- **Development**: `.env` or `.env.local`
- **Production**: AWS Secrets Manager or similar secure vault

### Initialization

```python
from app.services.heleket_client import HeleketClient

# Using config values (recommended)
client = HeleketClient()

# Or with explicit credentials
client = HeleketClient(
    project_url="https://api.heleket.com",
    merchant_id="merchant-123",
    api_key="api-key-456"
)
```

## Usage

### Creating a Payout

```python
from app.services.heleket_client import HeleketClient

client = HeleketClient()

# Generate idempotency key
idempotency_key = HeleketClient.generate_idempotency_key(
    client_id="client-123",
    asset="USDT",
    timestamp="2025-10-14T12:00:00"
)

# Create payout
success, response, error = client.create_payout(
    wallet_address="TRX1234567890abcdef",
    asset="USDT",
    network="TRON",
    amount=100.50,
    idempotency_key=idempotency_key,
    memo_tag=None,  # Optional, for networks that require it (e.g., XRP)
    metadata={"plan_id": "plan-456", "campaign": "bonus"}  # Optional
)

if success:
    transaction_id = response["transaction_id"]
    print(f"Payout created: {transaction_id}")
else:
    print(f"Error: {error}")
```

### Checking Payout Status

```python
success, response, error = client.get_payout_status("transaction-id-123")

if success:
    status = response["status"]
    print(f"Payout status: {status}")
```

### Canceling a Payout

```python
success, response, error = client.cancel_payout("transaction-id-123")

if success:
    print("Payout cancelled successfully")
```

## Idempotency

The client provides built-in idempotency key generation to prevent duplicate payouts:

```python
# Generate deterministic key
key = HeleketClient.generate_idempotency_key(
    client_id="client-123",
    asset="USDT",
    timestamp="2025-10-14T12:00:00"  # Optional, auto-generates if not provided
)
```

The key is a SHA256 hash of `{client_id}:{asset}:{timestamp}`, ensuring the same inputs always produce the same key.

## Error Handling

The client defines several exception types:

- `HeleketError`: Base exception
- `HeleketAuthenticationError`: Authentication/credentials issues
- `HeleketValidationError`: Request validation failures
- `HeleketNetworkError`: Network communication errors

All methods return a tuple: `(success: bool, data: Optional[dict], error: Optional[str])`

```python
success, data, error = client.create_payout(...)

if not success:
    if "Client error 400" in error:
        # Handle validation error
        pass
    elif "Request failed after" in error:
        # Handle network/retry exhaustion
        pass
```

## Retry Logic

The client automatically retries failed requests:

- **Max Retries**: 3 attempts (configurable)
- **Backoff Strategy**: Exponential (1s, 2s, 4s)
- **Retry Conditions**: Server errors (5xx), timeouts, connection errors
- **No Retry**: Client errors (4xx) are not retried

## Request Headers

All requests include:

```
Content-Type: application/json
X-Merchant-ID: {merchant_id}
X-API-Key: {api_key}
X-Idempotency-Key: {idempotency_key}  # When provided
```

## Webhook Signature Verification

```python
payload = request.json
signature = request.headers.get("X-Heleket-Signature")

if client.verify_webhook_signature(payload, signature):
    # Process webhook
    pass
```

**Note**: Signature verification implementation depends on Heleket's documentation and is currently a placeholder.

## Integration with ClientCryptoPayout Model

The client works seamlessly with the `ClientCryptoPayout` model:

```python
from app.services.heleket_client import HeleketClient
from app.models.client_crypto_payout import ClientCryptoPayout

# Create payout record
success, payout_id, error = ClientCryptoPayout.create(
    client_id=client_id,
    asset="USDT",
    network="TRON",
    amount=100.50,
    wallet_address="TRX123...",
    idempotency_key=idempotency_key,
    origin=ClientCryptoPayout.ORIGIN_MANUAL,
    created_by=admin_id
)

if success:
    # Initialize Heleket client
    heleket = HeleketClient()
    
    # Create payout via API
    api_success, response, api_error = heleket.create_payout(
        wallet_address="TRX123...",
        asset="USDT",
        network="TRON",
        amount=100.50,
        idempotency_key=idempotency_key
    )
    
    if api_success:
        # Update payout record with Heleket transaction ID
        ClientCryptoPayout.update_status(
            payout_id=payout_id,
            status=ClientCryptoPayout.STATUS_BROADCAST,
            heleket_transaction_id=response["transaction_id"],
            response_data=response
        )
        
        # Store the payload sent
        ClientCryptoPayout.update_heleket_payload(payout_id, response)
    else:
        # Mark as failed
        ClientCryptoPayout.update_status(
            payout_id=payout_id,
            status=ClientCryptoPayout.STATUS_FAILED,
            response_data={"error": api_error}
        )
```

## Testing

Unit tests with mocked responses:

```python
from unittest.mock import Mock, patch
from app.services.heleket_client import HeleketClient

@patch("app.services.heleket_client.requests.request")
def test_create_payout(mock_request):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"transaction_id": "tx-123"}
    mock_request.return_value = mock_response
    
    client = HeleketClient()
    success, data, error = client.create_payout(...)
    
    assert success is True
    assert data["transaction_id"] == "tx-123"
```

## Best Practices

1. **Always use idempotency keys** to prevent duplicate payouts
2. **Store Heleket responses** in `ClientCryptoPayout` for audit trail
3. **Handle errors gracefully** and log them appropriately
4. **Use environment variables** for credentials, never hardcode
5. **Monitor retry exhaustion** as it indicates API issues
6. **Validate wallet addresses** before sending to Heleket
7. **Test with sandbox credentials** before production deployment

## API Reference

### HeleketClient Methods

#### `__init__(project_url, merchant_id, api_key, timeout=30, max_retries=3)`
Initialize the Heleket API client.

#### `create_payout(wallet_address, asset, network, amount, idempotency_key, memo_tag=None, metadata=None)`
Create a cryptocurrency payout.

**Returns**: `Tuple[bool, Optional[Dict], Optional[str]]`

#### `get_payout_status(transaction_id)`
Get the status of a payout transaction.

**Returns**: `Tuple[bool, Optional[Dict], Optional[str]]`

#### `cancel_payout(transaction_id)`
Cancel a pending payout transaction.

**Returns**: `Tuple[bool, Optional[Dict], Optional[str]]`

#### `generate_idempotency_key(client_id, asset, timestamp=None)` (static)
Generate a deterministic idempotency key.

**Returns**: `str` (SHA256 hash)

#### `verify_webhook_signature(payload, signature)`
Verify webhook signature from Heleket.

**Returns**: `bool`

## Supported Networks and Assets

The client supports any combination that Heleket supports. Common examples:

- **USDT**: TRON, Ethereum, BSC, Polygon
- **BTC**: Bitcoin
- **ETH**: Ethereum
- **XRP**: Ripple (requires memo_tag)
- **And more...**

Refer to Heleket's documentation for the complete list of supported assets and networks.
