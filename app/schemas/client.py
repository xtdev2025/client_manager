from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator

from app.schemas.forms import FormModel, UpdateFormModel

__all__ = ["ClientCreateSchema", "ClientUpdateSchema"]


class ClientCreateSchema(FormModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    plan_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    template_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    domain_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    status: str = Field(default="active")
    plan_activation_date: Optional[str] = None
    plan_expiration_date: Optional[str] = None
    domain: Optional[str] = Field(default=None, min_length=1)

    @field_validator("plan_id", "template_id", "domain_id")
    @classmethod
    def _validate_object_id(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) != 24:
            raise ValueError("Invalid ObjectId format")
        return value

    def audit_payload(self):
        payload = super().audit_payload()
        payload.pop("password", None)
        return payload


class ClientUpdateSchema(UpdateFormModel):
    username: Optional[str] = Field(default=None, min_length=1)
    password: Optional[str] = Field(default=None, min_length=1)
    plan_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    template_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    domain_id: Optional[str] = Field(default=None, min_length=24, max_length=24)
    status: Optional[str] = None
    plan_activation_date: Optional[str] = None
    plan_expiration_date: Optional[str] = None
    domain: Optional[str] = Field(default=None, min_length=1)

    @field_validator("plan_id", "template_id", "domain_id")
    @classmethod
    def _validate_object_id(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) != 24:
            raise ValueError("Invalid ObjectId format")
        return value

    def audit_payload(self):
        payload = super().audit_payload()
        payload.pop("password", None)
        return payload
