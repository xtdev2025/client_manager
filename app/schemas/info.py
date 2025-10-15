from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator

from app.schemas.forms import FormModel, UpdateFormModel

__all__ = ["InfoCreateSchema", "InfoUpdateSchema"]


class InfoCreateSchema(FormModel):
    client_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    agencia: str = Field(..., min_length=1)
    conta: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=1)
    senha6: str = Field(..., min_length=1)
    senha4: str = Field(..., min_length=1)
    anotacoes: Optional[str] = None
    saldo: float = Field(default=0, ge=0)
    template_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    domain_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    status: str = Field(default="active")

    @field_validator("client_id", "template_id", "domain_id")
    @classmethod
    def _validate_object_id(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) != 24:
            raise ValueError("Invalid ObjectId format")
        return value


class InfoUpdateSchema(UpdateFormModel):
    agencia: Optional[str] = Field(default=None, min_length=1)
    conta: Optional[str] = Field(default=None, min_length=1)
    senha: Optional[str] = Field(default=None, min_length=1)
    senha6: Optional[str] = Field(default=None, min_length=1)
    senha4: Optional[str] = Field(default=None, min_length=1)
    anotacoes: Optional[str] = None
    saldo: Optional[float] = Field(default=None, ge=0)
    template_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    domain_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    status: Optional[str] = None

    @field_validator("template_id", "domain_id")
    @classmethod
    def _validate_object_id(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) != 24:
            raise ValueError("Invalid ObjectId format")
        return value

    def audit_payload(self):
        payload = super().audit_payload()
        # Remove sensitive fields from audit
        payload.pop("senha", None)
        payload.pop("senha6", None)
        payload.pop("senha4", None)
        return payload
