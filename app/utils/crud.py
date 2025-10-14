from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class CrudOperationResult:
    """Standard response wrapper for CRUD operations."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    @classmethod
    def ok(cls, data: Optional[Dict[str, Any]] = None, message: Optional[str] = None) -> "CrudOperationResult":
        return cls(success=True, data=data, message=message, errors=[])

    @classmethod
    def fail(
        cls,
        message: Optional[str] = None,
        errors: Optional[List[str]] = None,
    ) -> "CrudOperationResult":
        return cls(success=False, data=None, message=message, errors=list(errors or ([] if not message else [message])))

    def combine_errors(self, extra_errors: List[str]) -> None:
        self.errors.extend(extra_errors)

    def to_flash(self, success_category: str = "success", error_category: str = "danger") -> tuple[str, str]:
        category = success_category if self.success else error_category
        if self.message:
            return category, self.message
        if self.errors:
            return category, "; ".join(self.errors)
        return category, "Operation completed" if self.success else "Operation failed"
