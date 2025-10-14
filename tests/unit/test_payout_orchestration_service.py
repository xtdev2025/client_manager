"""Testes unitários para PayoutOrchestrationService."""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import pytest
from bson.objectid import ObjectId

from app import mongo, bcrypt
from app.models.client_crypto_payout import ClientCryptoPayout
from app.services.payout_orchestration_service import PayoutOrchestrationService


class DummyHeleketClient:
    """Cliente Heleket de teste com comportamento configurável."""

    def __init__(self, *, should_succeed: bool = True, response: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.should_succeed = should_succeed
        self.response = response or {"status": "confirmed", "transaction_id": "tx-123"}
        self.error = error or "Erro simulado"
        self.calls = []

    def create_payout(
        self,
        *,
        wallet_address: str,
        asset: str,
        network: str,
        amount: float,
        idempotency_key: str,
        memo_tag: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        payload = {
            "wallet_address": wallet_address,
            "asset": asset,
            "network": network,
            "amount": amount,
            "idempotency_key": idempotency_key,
            "memo_tag": memo_tag,
            "metadata": metadata,
        }
        self.calls.append(payload)
        if self.should_succeed:
            return True, self.response, None
        return False, None, self.error


@pytest.fixture
def payout_context(app, clean_db):
    """Prepara dados mínimos de cliente para testes do serviço."""
    with app.app_context():
        now = datetime.utcnow()
        client_id = ObjectId()
        mongo.db.clients.insert_one(
            {
                "_id": client_id,
                "username": "cliente-test",
                "status": "active",
                "createdAt": now,
                "updatedAt": now,
            }
        )
        created_by = ObjectId()
        mongo.db.admins.insert_one(
            {
                "_id": created_by,
                "username": "admin-test",
                "password": bcrypt.generate_password_hash("Senha@123").decode("utf-8"),
                "role": "admin",
                "createdAt": now,
                "updatedAt": now,
            }
        )

        yield {
            "client_id": client_id,
            "created_by": created_by,
        }


def _call_service(app, payload: Dict[str, Any], heleket_client: DummyHeleketClient):
    with app.app_context():
        return PayoutOrchestrationService.initiate_payout(
            heleket_client=heleket_client,
            **payload,
        )


def test_initiate_payout_success(app, payout_context):
    heleket_client = DummyHeleketClient(response={"status": "confirmed", "transaction_id": "tx-999"})
    payload = {
        "client_id": payout_context["client_id"],
        "asset": "USDT",
        "network": "TRON",
        "amount": 150.0,
        "wallet_address": "TRX123",
        "created_by": payout_context["created_by"],
    }

    success, data, error = _call_service(app, payload, heleket_client)

    assert success is True
    assert error is None
    assert data["status"] == "confirmed"
    assert data["heleket_transaction_id"] == "tx-999"
    assert len(heleket_client.calls) == 1

    payout = ClientCryptoPayout.get_by_id(data["payout_id"])
    assert payout is not None
    assert payout["created_by"] == payout_context["created_by"]
    assert payout["status"] == "confirmed"
    assert payout["heleket_transaction_id"] == "tx-999"


def test_initiate_payout_idempotent(app, payout_context):
    heleket_client = DummyHeleketClient()
    idempotency_key = "idem-123"
    payload = {
        "client_id": str(payout_context["client_id"]),
        "asset": "USDT",
        "network": "TRON",
        "amount": 200,
        "wallet_address": "TRXABC",
        "created_by": str(payout_context["created_by"]),
        "idempotency_key": idempotency_key,
    }

    success_first, data_first, error_first = _call_service(app, payload, heleket_client)
    assert success_first is True
    assert error_first is None

    # Segunda chamada deve ser idempotente e não invocar o cliente Heleket novamente
    heleket_client.calls.clear()
    success_second, data_second, error_second = _call_service(app, payload, heleket_client)

    assert success_second is True
    assert error_second is None
    assert data_second["payout_id"] == data_first["payout_id"]
    assert heleket_client.calls == []


def test_initiate_payout_api_failure(app, payout_context):
    heleket_client = DummyHeleketClient(should_succeed=False, error="Falha na API")
    payload = {
        "client_id": payout_context["client_id"],
        "asset": "USDT",
        "network": "TRON",
        "amount": 300,
        "wallet_address": "TRXFAIL",
        "created_by": payout_context["created_by"],
    }

    success, data, error = _call_service(app, payload, heleket_client)

    assert success is False
    assert data["status"] == ClientCryptoPayout.STATUS_FAILED
    assert "Falha" in error

    payout = ClientCryptoPayout.get_by_id(data["payout_id"])
    assert payout is not None
    assert payout["status"] == ClientCryptoPayout.STATUS_FAILED
    assert payout["responseLogs"]