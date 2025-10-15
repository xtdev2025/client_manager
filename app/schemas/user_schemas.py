"""Backward-compatible imports for legacy modules.

Prefer importing from the specific modules in ``app.schemas`` instead of this
aggregated module.
"""

from __future__ import annotations

import warnings

from app.schemas.admin import AdminCreateSchema
from app.schemas.auth import LoginSchema
from app.schemas.client import ClientCreateSchema
from app.schemas.domain import DomainCreateSchema
from app.schemas.plan import PlanCreateSchema
from app.schemas.user import UserCreateSchema, UserUpdateSchema

__all__ = [
    "UserCreateSchema",
    "UserUpdateSchema",
    "AdminCreateSchema",
    "ClientCreateSchema",
    "LoginSchema",
    "PlanCreateSchema",
    "DomainCreateSchema",
]

warnings.warn(
    "app.schemas.user_schemas is deprecated; import from the specific modules in app.schemas instead",
    DeprecationWarning,
    stacklevel=2,
)
