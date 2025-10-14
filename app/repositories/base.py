from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from app.utils.crud import CrudOperationResult


class CrudRepositoryProtocol(Protocol):
    """Protocol describing the expected CRUD interface for repositories."""

    def get_all(self) -> list[Any]:
        ...

    def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        ...

    def create(self, data: Dict[str, Any]) -> CrudOperationResult:
        ...

    def update(self, entity_id: str, data: Dict[str, Any]) -> CrudOperationResult:
        ...

    def delete(self, entity_id: str) -> CrudOperationResult:
        ...


@dataclass(slots=True)
class ModelCrudRepository(CrudRepositoryProtocol):
    """Adapter that wraps existing model classes exposing a consistent CRUD contract."""

    model: Any

    def get_all(self) -> list[Any]:
        return list(self.model.get_all())

    def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.model.get_by_id(entity_id)

    def create(self, data: Dict[str, Any]) -> CrudOperationResult:
        success, payload = self.model.create(**data)
        if success:
            entity_id = self._extract_identifier(payload, data)
            entity = self.get_by_id(entity_id) if entity_id else None
            return CrudOperationResult.ok(data=entity, message="Created successfully")
        return CrudOperationResult.fail(message=str(payload))

    def update(self, entity_id: str, data: Dict[str, Any]) -> CrudOperationResult:
        success, payload = self.model.update(entity_id, data)
        if success:
            entity = self.get_by_id(entity_id)
            return CrudOperationResult.ok(data=entity, message=str(payload))
        return CrudOperationResult.fail(message=str(payload))

    def delete(self, entity_id: str) -> CrudOperationResult:
        success, payload = self.model.delete(entity_id)
        if success:
            return CrudOperationResult.ok(data={"_id": entity_id}, message=str(payload))
        return CrudOperationResult.fail(message=str(payload))

    @staticmethod
    def _extract_identifier(payload: Any, data: Dict[str, Any]) -> Optional[str]:
        if isinstance(payload, dict):
            if "_id" in payload:
                return str(payload["_id"])
            if "id" in payload:
                return str(payload["id"])
        if isinstance(payload, (str, int)):
            return str(payload)
        return data.get("_id") or data.get("id")
