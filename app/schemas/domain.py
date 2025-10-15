from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator

from app.schemas.forms import FormModel, UpdateFormModel

__all__ = ["DomainCreateSchema", "DomainUpdateSchema"]


class DomainCreateSchema(FormModel):
    name: str = Field(..., min_length=1)
    cloudflare_api: Optional[str] = None
    cloudflare_email: Optional[str] = None
    cloudflare_password: Optional[str] = None
    cloudflare_status: bool = False
    ssl: bool = False
    domain_limit: int = Field(5, ge=1)

    @field_validator("cloudflare_status", mode="before")
    @classmethod
    def _normalize_cloudflare_status(cls, value):
        return FormModel.normalize_bool(value)

    @field_validator("ssl", mode="before")
    @classmethod
    def _normalize_ssl(cls, value):
        return FormModel.normalize_bool(value)


class DomainUpdateSchema(UpdateFormModel):
    name: Optional[str] = Field(None, min_length=1)
    cloudflare_api: Optional[str] = None
    cloudflare_email: Optional[str] = None
    cloudflare_password: Optional[str] = None
    cloudflare_status: Optional[bool] = None
    ssl: Optional[bool] = None
    domain_limit: Optional[int] = Field(None, ge=1)

    @field_validator("cloudflare_status", mode="before")
    @classmethod
    def _normalize_cloudflare_status(cls, value):
        if value is None:
            return None
        return FormModel.normalize_bool(value)

    @field_validator("ssl", mode="before")
    @classmethod
    def _normalize_ssl(cls, value):
        if value is None:
            return None
        return FormModel.normalize_bool(value)
