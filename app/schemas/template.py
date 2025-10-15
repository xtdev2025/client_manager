from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.schemas.forms import FormModel, UpdateFormModel

__all__ = ["TemplateCreateSchema", "TemplateUpdateSchema"]


class TemplateCreateSchema(FormModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    content: str = Field("{}")
    status: str = Field("active")


class TemplateUpdateSchema(UpdateFormModel):
    name: Optional[str] = Field(None, min_length=1)
    slug: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    def audit_payload(self):
        return super().audit_payload()
