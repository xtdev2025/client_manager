"""Serviço responsável por orquestrar pagamentos Heleket."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from bson.objectid import ObjectId
from flask import current_app

from app.models.client import Client
from app.models.client_crypto_payout import ClientCryptoPayout
from app.services.heleket_client import HeleketClient, HeleketError


class PayoutOrchestrationService:
  """Coordenador de requisições de payout junto ao Heleket."""

  @staticmethod
  def initiate_payout(
    *,
    client_id: Any,
    asset: str,
    network: str,
    amount: Any,
    wallet_address: str,
    created_by: Any,
    origin: str = ClientCryptoPayout.ORIGIN_MANUAL,
    memo_tag: Optional[str] = None,
    wallet_profile_id: Optional[Any] = None,
    trigger_metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
    heleket_client: Optional[HeleketClient] = None,
  ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Inicia um payout e integra com Heleket."""

    # Validações básicas de argumentos obrigatórios
    if not client_id:
      return False, None, "client_id é obrigatório"
    if not created_by:
      return False, None, "created_by é obrigatório"
    if not asset:
      return False, None, "asset é obrigatório"
    if not network:
      return False, None, "network é obrigatório"
    if not wallet_address:
      return False, None, "wallet_address é obrigatório"

    try:
      amount_value = float(amount)
    except (TypeError, ValueError):
      return False, None, "amount deve ser numérico"

    if amount_value <= 0:
      return False, None, "amount deve ser maior que zero"

    if origin not in ClientCryptoPayout.VALID_ORIGINS:
      return False, None, "origin inválido"

    # Conversão de IDs para ObjectId quando aplicável
    try:
      client_obj_id = client_id if isinstance(client_id, ObjectId) else ObjectId(str(client_id))
    except Exception:  # pragma: no cover - feedback direto ao usuário
      return False, None, "client_id inválido"

    try:
      created_by_obj_id = created_by if isinstance(created_by, ObjectId) else ObjectId(str(created_by))
    except Exception:
      return False, None, "created_by inválido"

    wallet_profile_obj_id: Optional[ObjectId] = None
    if wallet_profile_id:
      try:
        wallet_profile_obj_id = (
          wallet_profile_id
          if isinstance(wallet_profile_id, ObjectId)
          else ObjectId(str(wallet_profile_id))
        )
      except Exception:
        return False, None, "wallet_profile_id inválido"

    # Confirma cliente existente e ativo
    client = Client.get_by_id(client_obj_id)
    if not client:
      return False, None, "Cliente não encontrado"
    if client.get("status") not in {"active", "trial"}:
      return False, None, "Cliente inativo"

    # Idempotência: gera chave caso não seja informada
    if not idempotency_key:
      timestamp = datetime.utcnow().isoformat()
      idempotency_key = HeleketClient.generate_idempotency_key(str(client_obj_id), asset, timestamp)

    existing_payout = ClientCryptoPayout.get_by_idempotency_key(idempotency_key)
    if existing_payout:
      payout_snapshot = PayoutOrchestrationService._build_snapshot(existing_payout)
      return True, payout_snapshot, None

    trigger_metadata = trigger_metadata or {}
    metadata = metadata or {}

    heleket_client = heleket_client or HeleketClient()

    success, payout_id, creation_error = ClientCryptoPayout.create(
      client_id=client_obj_id,
      asset=asset,
      network=network,
      amount=amount_value,
      wallet_address=wallet_address,
      idempotency_key=idempotency_key,
      origin=origin,
      wallet_profile_id=wallet_profile_obj_id,
      memo_tag=memo_tag,
      trigger_metadata=trigger_metadata,
      created_by=created_by_obj_id,
    )

    if not success or payout_id is None:
      return False, None, creation_error

    heleket_payload = {
      "wallet_address": wallet_address,
      "asset": asset,
      "network": network,
      "amount": amount_value,
    }

    if memo_tag:
      heleket_payload["memo_tag"] = memo_tag

    metadata_payload = {**metadata}
    metadata_payload.setdefault("client_id", str(client_obj_id))
    metadata_payload.setdefault("origin", origin)
    if trigger_metadata:
      metadata_payload["trigger"] = PayoutOrchestrationService._stringify_ids(trigger_metadata)

    if metadata_payload:
      heleket_payload["metadata"] = metadata_payload

    ClientCryptoPayout.update_heleket_payload(payout_id, heleket_payload)

    try:
      api_success, api_response, api_error = heleket_client.create_payout(
        wallet_address=wallet_address,
        asset=asset,
        network=network,
        amount=amount_value,
        idempotency_key=idempotency_key,
        memo_tag=memo_tag,
        metadata=metadata_payload if metadata_payload else None,
      )
    except HeleketError as exc:  # pragma: no cover - exceções específicas do client
      api_success, api_response, api_error = False, None, str(exc)

    if not api_success:
      error_payload = {"error": api_error or "Erro desconhecido"}
      ClientCryptoPayout.update_status(
        payout_id=payout_id,
        status=ClientCryptoPayout.STATUS_FAILED,
        response_data=error_payload,
        status_source="orchestration",
        status_details={"stage": "initiate", "error": api_error} if api_error else {"stage": "initiate"},
        extra_fields={
          "failureReason": api_error,
          "lastStatusCheckAt": datetime.utcnow(),
          "lastStatusCheckSource": "orchestration",
          "nextStatusCheckAt": None,
        },
      )

      failure_snapshot = {
        "payout_id": payout_id,
        "idempotency_key": idempotency_key,
        "status": ClientCryptoPayout.STATUS_FAILED,
      }

      return False, failure_snapshot, api_error

    heleket_status = api_response.get("status") if api_response else None
    if heleket_status not in ClientCryptoPayout.VALID_STATUSES:
      heleket_status = ClientCryptoPayout.STATUS_BROADCAST

    transaction_id = None
    if api_response:
      transaction_id = api_response.get("transaction_id") or api_response.get("id")
      if not transaction_id and isinstance(api_response.get("data"), dict):
        transaction_id = api_response["data"].get("transaction_id")

    ClientCryptoPayout.update_status(
      payout_id=payout_id,
      status=heleket_status,
      heleket_transaction_id=transaction_id,
      response_data=api_response,
      status_source="orchestration",
      status_details={"stage": "initiate", "raw_status": api_response.get("status") if api_response else None},
      extra_fields={
        "lastStatusCheckAt": datetime.utcnow(),
        "lastStatusCheckSource": "orchestration",
      },
    )

    payout_snapshot = {
      "payout_id": payout_id,
      "status": heleket_status,
      "heleket_transaction_id": transaction_id,
      "idempotency_key": idempotency_key,
    }

    current_app.logger.info(
      "Payout %s orquestrado com status %s", payout_id, heleket_status
    )

    return True, payout_snapshot, None

  @staticmethod
  def _build_snapshot(document: Dict[str, Any]) -> Dict[str, Any]:
    """Cria uma visão resumida do payout para retornos do serviço."""
    return {
      "payout_id": str(document.get("_id")),
      "status": document.get("status"),
      "heleket_transaction_id": document.get("heleket_transaction_id"),
      "idempotency_key": document.get("idempotency_key"),
    }

  @staticmethod
  def _stringify_ids(value: Any) -> Any:
    """Converte ObjectIds aninhados em strings para metadados serializáveis."""
    if isinstance(value, ObjectId):
      return str(value)
    if isinstance(value, list):
      return [PayoutOrchestrationService._stringify_ids(item) for item in value]
    if isinstance(value, dict):
      return {key: PayoutOrchestrationService._stringify_ids(val) for key, val in value.items()}
    return value
