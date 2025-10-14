from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.audit_service import AuditService


def log_change(
    entity: str,
    action: str,
    entity_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Generic audit logger that enforces a consistent detail structure."""

    details: Dict[str, Any] = {"payload": payload or {}}
    if metadata:
        details["metadata"] = metadata

    return AuditService.log_action(
        action=action,
        entity_type=entity,
        entity_id=entity_id,
        details=details,
    )


def log_creation(entity: str, entity_id: Optional[str], payload: Dict[str, Any]) -> bool:
    return log_change(entity=entity, action="create", entity_id=entity_id, payload=payload)


def log_update(entity: str, entity_id: Optional[str], payload: Dict[str, Any]) -> bool:
    return log_change(entity=entity, action="update", entity_id=entity_id, payload=payload)


def log_deletion(entity: str, entity_id: Optional[str], payload: Optional[Dict[str, Any]] = None) -> bool:
    return log_change(entity=entity, action="delete", entity_id=entity_id, payload=payload or {})
