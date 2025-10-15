"""Backward-compatible shim for legacy imports.

Prefer importing from the dedicated modules in ``app.schemas`` (e.g.
``app.schemas.plan``) instead of this module.
"""

from __future__ import annotations

import warnings

from app.schemas.client import ClientCreateSchema, ClientUpdateSchema
from app.schemas.domain import DomainCreateSchema, DomainUpdateSchema
from app.schemas.forms import FormModel, UpdateFormModel, parse_form
from app.schemas.info import InfoCreateSchema, InfoUpdateSchema
from app.schemas.plan import PlanCreateSchema, PlanUpdateSchema
from app.schemas.template import TemplateCreateSchema, TemplateUpdateSchema

__all__ = [
    "FormModel",
    "UpdateFormModel",
    "parse_form",
    "PlanCreateSchema",
    "PlanUpdateSchema",
    "DomainCreateSchema",
    "DomainUpdateSchema",
    "TemplateCreateSchema",
    "TemplateUpdateSchema",
    "InfoCreateSchema",
    "InfoUpdateSchema",
    "ClientCreateSchema",
    "ClientUpdateSchema",
]

warnings.warn(
    "app.schemas.crud is deprecated; import from the specific modules in app.schemas instead",
    DeprecationWarning,
    stacklevel=2,
)
