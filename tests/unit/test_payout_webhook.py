"""Unit tests for Heleket payout webhook endpoint."""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from app import mongo
from app.models.client_crypto_payout import ClientCryptoPayout


def _prepare_payout():
    client = mongo.db.clients.find_one({"username": "cliente1"})
    assert client is not None

    success, payout_id, error = ClientCryptoPayout.create(
        client_id=client["_id"],
        asset="USDT",
        network="TRON",
        amount=100.0,
        wallet_address="TLExample",
        idempotency_key="idem-123",
        origin=ClientCryptoPayout.ORIGIN_MANUAL,
        created_by=None,
    )

    assert success is True, error
    return payout_id


@pytest.mark.unit
def test_webhook_updates_payout_status(client, test_app):
    secret = "topsecret"
    test_app.config["HELEKET_WEBHOOK_SECRET"] = secret

    with test_app.app_context():
        payout_id = _prepare_payout()

    payload = {
        "idempotency_key": "idem-123",
        "status": "confirmed",
        "transaction_id": "tx-789",
    }
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    response = client.post(
        "/payouts/webhook",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Heleket-Signature": signature,
        },
    )

    assert response.status_code == 200
    assert response.json["success"] is True

    with test_app.app_context():
        payout_doc = ClientCryptoPayout.get_by_id(payout_id)
        assert payout_doc is not None
        assert payout_doc["status"] == ClientCryptoPayout.STATUS_CONFIRMED
        assert payout_doc.get("heleket_transaction_id") == "tx-789"
        assert payout_doc.get("lastWebhookAt") is not None

        audit_entry = mongo.db.audit_logs.find_one({"entity_id": payout_id})
        assert audit_entry is not None
        assert audit_entry.get("action") == "webhook"


@pytest.mark.unit
def test_webhook_rejects_invalid_signature(client, test_app):
    test_app.config["HELEKET_WEBHOOK_SECRET"] = "anothersecret"

    response = client.post(
        "/payouts/webhook",
        data=json.dumps({"status": "failed"}),
        headers={"Content-Type": "application/json", "X-Heleket-Signature": "invalid"},
    )

    assert response.status_code == 400
    assert response.json["error"] == "invalid_signature"


@pytest.mark.unit
def test_webhook_health_reports_configured_secret(client, test_app):
    test_app.config["HELEKET_WEBHOOK_SECRET"] = "configured"

    response = client.get("/payouts/webhook/health")

    assert response.status_code == 200
    assert response.json["secret_configured"] is True
    assert response.json["status"] == "ok"


@pytest.mark.unit
def test_webhook_health_reports_missing_secret(client, test_app):
    test_app.config.pop("HELEKET_WEBHOOK_SECRET", None)

    response = client.get("/payouts/webhook/health")

    assert response.status_code == 503
    assert response.json["secret_configured"] is False
    assert response.json["status"] == "misconfigured"