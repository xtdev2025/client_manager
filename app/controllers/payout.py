"""Payout-related routes such as Heleket webhooks."""

from __future__ import annotations

from datetime import datetime
import hashlib
import hmac
from typing import Any, Dict, Optional

from flask import Blueprint, Response, current_app, jsonify, request
from flask_login import login_required

from app import csrf
from app.models.client_crypto_payout import ClientCryptoPayout
from app.services.audit_helper import log_change
from app.services.payout_reconciliation_service import PayoutReconciliationService
from app.controllers.auth import admin_required


payout = Blueprint("payout", __name__, url_prefix="/payouts")
csrf.exempt(payout)


def _normalize_signature(signature: Optional[str]) -> Optional[str]:
    if not signature:
        return None
    signature = signature.strip()
    if signature.startswith("sha256="):
        signature = signature.split("=", 1)[1]
    return signature or None


def _validate_signature(raw_body: bytes, provided_signature: Optional[str]) -> bool:
    secret = current_app.config.get("HELEKET_WEBHOOK_SECRET")
    if not secret:
        current_app.logger.warning("HELEKET_WEBHOOK_SECRET não configurado; aceitando webhook sem validação.")
        return True

    signature = _normalize_signature(provided_signature)
    if not signature:
        return False

    expected_signature = hmac.new(
        secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def _resolve_target_payout(event_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    idempotency_key = event_payload.get("idempotency_key")
    transaction_id = event_payload.get("transaction_id") or event_payload.get("heleket_transaction_id")

    payout_document = None
    if idempotency_key:
        payout_document = ClientCryptoPayout.get_by_idempotency_key(idempotency_key)

    if not payout_document and transaction_id:
        payout_document = ClientCryptoPayout.get_by_transaction_id(transaction_id)

    return payout_document


def _map_status(status: Optional[str]) -> Optional[str]:
    return ClientCryptoPayout.normalize_status(status)


@payout.route("/webhook/health", methods=["GET"])
def webhook_health() -> Response:
    secret_configured = bool(current_app.config.get("HELEKET_WEBHOOK_SECRET"))

    payload = {
        "status": "ok" if secret_configured else "misconfigured",
        "webhook": "heleket",
        "secret_configured": secret_configured,
    }

    return jsonify(payload), 200 if secret_configured else 503


@payout.route("/webhook", methods=["POST"])
def handle_webhook() -> Response:
    raw_body = request.data or b""
    provided_signature = request.headers.get("X-Heleket-Signature")

    if not _validate_signature(raw_body, provided_signature):
        current_app.logger.warning("Webhook Heleket com assinatura inválida ou ausente.")
        return jsonify({"success": False, "error": "invalid_signature"}), 400

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        current_app.logger.warning("Webhook Heleket sem payload JSON válido.")
        return jsonify({"success": False, "error": "invalid_payload"}), 400

    payout_document = _resolve_target_payout(payload)
    if not payout_document:
        current_app.logger.warning("Webhook Heleket recebido, mas payout não localizado.")
        return jsonify({"success": False, "error": "payout_not_found"}), 404

    payout_id = str(payout_document.get("_id"))
    status = _map_status(payload.get("status")) or payout_document.get("status")
    transaction_id = payload.get("transaction_id") or payload.get("heleket_transaction_id")

    success, error_message = ClientCryptoPayout.update_status(
        payout_id=payout_id,
        status=status,
        heleket_transaction_id=transaction_id,
        response_data={
            "source": "webhook",
            "payload": payload,
        },
        status_source="webhook",
        status_details={"raw_status": payload.get("status"), "event": payload.get("event")},
        extra_fields={
            "lastStatusCheckAt": datetime.utcnow(),
            "lastStatusCheckSource": "webhook",
        },
    )

    if not success:
        current_app.logger.error(
            "Falha ao atualizar payout %s com dados do webhook: %s", payout_id, error_message
        )
        return jsonify({"success": False, "error": "update_failed"}), 500

    ClientCryptoPayout.mark_webhook_received(payout_id)

    log_change(
        "payout",
        "webhook",
        entity_id=payout_id,
        payload={
            "status": status,
            "heleket_transaction_id": transaction_id,
        },
        actor_user_id="heleket_webhook",
        ip_address=request.remote_addr,
    )

    return jsonify({"success": True, "payout_id": payout_id, "status": status})


@payout.route("/reconcile", methods=["POST"])
@login_required
@admin_required
def reconcile_now() -> Response:
    payload = request.get_json(silent=True) or {}

    def _int_config(value: Optional[Any], default: Optional[int] = None) -> Optional[int]:
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    limit = _int_config(payload.get("limit"), 50)
    min_delay = _int_config(payload.get("min_delay"))
    interval = _int_config(payload.get("interval"))
    alert_attempts = _int_config(payload.get("alert_attempts"))
    alert_age = _int_config(payload.get("alert_age"))
    lookback = _int_config(payload.get("lookback"))

    results = PayoutReconciliationService.schedule_pending(
        limit=limit or 50,
        min_delay_minutes=min_delay,
        poll_interval_minutes=interval,
        alert_attempts=alert_attempts,
        alert_age_minutes=alert_age,
        lookback_days=lookback,
    )

    log_change(
        "payout",
        "reconcile_manual",
        entity_id=None,
        payload={
            "results": results,
            "limit": limit,
            "min_delay": min_delay,
            "interval": interval,
            "alert_attempts": alert_attempts,
            "alert_age": alert_age,
            "lookback": lookback,
        },
    )

    return jsonify({"success": True, "results": results})
