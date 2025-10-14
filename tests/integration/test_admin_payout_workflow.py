"""Integration tests for admin payout workflow UI."""

from __future__ import annotations

from typing import Dict

import pytest

from app import mongo


def _login_admin(client) -> None:
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "Admin@123"},
        follow_redirects=True,
    )
    assert response.status_code == 200


@pytest.mark.integration
def test_admin_initiates_payout_success(client, test_app, monkeypatch):
    _login_admin(client)

    with test_app.app_context():
        client_document = mongo.db.clients.find_one({"username": "cliente1"})
        assert client_document is not None
        client_id = str(client_document["_id"])

    captured_call: Dict[str, Dict] = {}

    def _fake_initiate_payout(**kwargs):
        captured_call["kwargs"] = kwargs
        return True, {"payout_id": "abc123", "status": "broadcast"}, None

    monkeypatch.setattr(
        "app.controllers.client.PayoutOrchestrationService.initiate_payout",
        _fake_initiate_payout,
    )

    response = client.post(
        f"/clients/{client_id}/payouts/initiate",
        data={
            "asset": "usdt",
            "network": "tron",
            "amount": "150.50",
            "wallet_address": "TL5ExampleWalletAddress",
            "memo_tag": "optional-tag",
            "remember_wallet": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("#payouts")

    assert captured_call["kwargs"]["asset"] == "USDT"
    assert captured_call["kwargs"]["network"] == "TRON"
    assert captured_call["kwargs"]["amount"] == pytest.approx(150.50)

    with test_app.app_context():
        updated_client = mongo.db.clients.find_one({"_id": client_document["_id"]})
        prefs = updated_client.get("crypto_wallet_preferences")
        assert prefs == {
            "asset": "USDT",
            "network": "TRON",
            "wallet_address": "TL5ExampleWalletAddress",
            "memo_tag": "optional-tag",
            "default_amount": 150.5,
        }


@pytest.mark.integration
def test_admin_initiates_payout_failure(client, test_app, monkeypatch):
    _login_admin(client)

    with test_app.app_context():
        client_document = mongo.db.clients.find_one({"username": "cliente1"})
        assert client_document is not None
        client_id = str(client_document["_id"])

    def _fake_initiate_payout(**kwargs):
        return False, None, "Erro ao integrar com Heleket"

    monkeypatch.setattr(
        "app.controllers.client.PayoutOrchestrationService.initiate_payout",
        _fake_initiate_payout,
    )

    response = client.post(
        f"/clients/{client_id}/payouts/initiate",
        data={
            "asset": "USDT",
            "network": "TRON",
            "amount": "25",
            "wallet_address": "TL5ExampleWalletAddress",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Erro ao integrar com Heleket" in response.data


@pytest.mark.integration
def test_admin_triggers_reconciliation_endpoint(client, test_app, monkeypatch):
    _login_admin(client)

    monkeypatch.setattr(
        "app.controllers.payout.PayoutReconciliationService.schedule_pending",
        lambda **kwargs: {"checked": 2, "finalized": 1, "alerts": 0, "errors": 0},
    )

    response = client.post("/payouts/reconcile", json={"limit": 10})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["results"]["checked"] == 2