"""Integration tests for admin dashboard analytics endpoints."""

from __future__ import annotations

import pytest

from app import mongo
from app.models.client_crypto_payout import ClientCryptoPayout


def _login_admin(client) -> None:
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "Admin@123"},
        follow_redirects=True,
    )
    assert response.status_code == 200


@pytest.mark.integration
def test_admin_stats_includes_payout_metrics(client, test_app):
    """Ensure admin stats payload returns payout KPIs."""
    _login_admin(client)

    with test_app.app_context():
        client_document = mongo.db.clients.find_one({"username": "cliente1"})
        assert client_document is not None
        client_id = client_document["_id"]

        # Pending payout
        success, pending_id, error = ClientCryptoPayout.create(
            client_id=client_id,
            asset="USDT",
            network="TRON",
            amount=100,
            wallet_address="TPendingExample",
            idempotency_key="stats-pending-1",
        )
        assert success is True, error

        # Broadcast payout (still considered pending analytics)
        success, broadcast_id, error = ClientCryptoPayout.create(
            client_id=client_id,
            asset="USDT",
            network="TRON",
            amount=50,
            wallet_address="TBroadcastExample",
            idempotency_key="stats-broadcast-1",
        )
        assert success is True, error
        ClientCryptoPayout.update_status(
            broadcast_id,
            ClientCryptoPayout.STATUS_BROADCAST,
        )

        # Confirmed payout
        success, confirmed_id, error = ClientCryptoPayout.create(
            client_id=client_id,
            asset="USDT",
            network="TRON",
            amount=200,
            wallet_address="TConfirmedExample",
            idempotency_key="stats-confirmed-1",
        )
        assert success is True, error
        ClientCryptoPayout.update_status(
            confirmed_id,
            ClientCryptoPayout.STATUS_CONFIRMED,
        )

        # Failed payout
        success, failed_id, error = ClientCryptoPayout.create(
            client_id=client_id,
            asset="USDT",
            network="TRON",
            amount=75,
            wallet_address="TFailedExample",
            idempotency_key="stats-failed-1",
        )
        assert success is True, error
        ClientCryptoPayout.update_status(
            failed_id,
            ClientCryptoPayout.STATUS_FAILED,
        )

    response = client.get("/dashboard/api/admin-stats")

    assert response.status_code == 200
    data = response.get_json()

    payout_summary = data["payout_summary"]
    assert payout_summary["total_count"] == 4
    assert payout_summary["pending"]["count"] == 2
    assert payout_summary["confirmed"]["count"] == 1
    assert payout_summary["failed"]["count"] == 1
    assert pytest.approx(payout_summary["total_amount"], rel=1e-3) == 425
    assert pytest.approx(payout_summary["confirmed"]["amount"], rel=1e-3) == 200

    payout_distribution = data["payout_distribution"]
    assert payout_distribution["labels"] == ["Pendentes", "Confirmados", "Falhos"]
    assert payout_distribution["datasets"][0]["data"] == [2, 1, 1]

    payout_raw = data["payout_raw"]
    assert payout_raw["by_status"][ClientCryptoPayout.STATUS_BROADCAST]["count"] == 1
    assert payout_raw["by_status"][ClientCryptoPayout.STATUS_PENDING]["count"] == 1