from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    value_str = str(value).strip().lower()
    return value_str in {"1", "true", "yes", "on"}


class FormModel(BaseModel):
    """Base Pydantic model with helpers for parsing Flask request forms."""

    model_config = {
        "extra": "ignore",
        "str_strip_whitespace": True,
        "str_min_length": 0,
    }

    @field_validator("*", mode="before")
    @classmethod
    def _empty_string_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @classmethod
    def from_form(cls, form: Any) -> "FormModel":
        raw_data: Dict[str, Any] = {}
        for field in cls.model_fields:
            if hasattr(form, "getlist"):
                values = form.getlist(field)
                if len(values) > 1:
                    raw_data[field] = values
                    continue
            raw_data[field] = form.get(field)
        return cls.model_validate(raw_data)

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def audit_payload(self) -> Dict[str, Any]:
        return {key: value for key, value in self.model_dump().items() if value is not None}


class PlanCreateSchema(FormModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)


class PlanUpdateSchema(FormModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None


class DomainCreateSchema(FormModel):
    name: str = Field(..., min_length=1)
    cloudflare_api: Optional[str] = None
    cloudflare_email: Optional[str] = None
    cloudflare_password: Optional[str] = None
    cloudflare_status: bool = False
    ssl: bool = False
    domain_limit: int = Field(5, ge=1)

    _bool_cloudflare_status = field_validator("cloudflare_status", mode="before")(_normalize_bool)
    _bool_ssl = field_validator("ssl", mode="before")(_normalize_bool)


class DomainUpdateSchema(DomainCreateSchema):
    name: Optional[str] = Field(None, min_length=1)
    domain_limit: Optional[int] = Field(None, ge=1)


class TemplateCreateSchema(FormModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    content: str = Field("{}")
    status: str = Field("active")


class TemplateUpdateSchema(FormModel):
    name: Optional[str] = Field(None, min_length=1)
    slug: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class InfoCreateSchema(FormModel):
    agencia: str = Field(..., min_length=1)
    conta: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=1)
    senha6: str = Field(..., min_length=1)
    senha4: str = Field(..., min_length=1)
    anotacoes: Optional[str] = None
    saldo: float = Field(0, ge=0)
    template_id: Optional[str] = None
    domain_id: Optional[str] = None
    status: str = Field("active")


class InfoUpdateSchema(InfoCreateSchema):
    agencia: Optional[str] = Field(None, min_length=1)
    conta: Optional[str] = Field(None, min_length=1)
    senha: Optional[str] = Field(None, min_length=1)
    senha6: Optional[str] = Field(None, min_length=1)
    senha4: Optional[str] = Field(None, min_length=1)
    saldo: Optional[float] = Field(None, ge=0)


class ClientCreateSchema(FormModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    plan_id: Optional[str] = None
    template_id: Optional[str] = None
    domain_id: Optional[str] = None
    status: str = Field("active")
    plan_activation_date: Optional[str] = None
    plan_expiration_date: Optional[str] = None
    domain: Optional[str] = Field(None, min_length=1)

    def audit_payload(self) -> Dict[str, Any]:
        payload = super().audit_payload()
        payload.pop("password", None)
        return payload


class ClientUpdateSchema(FormModel):
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=1)
    plan_id: Optional[str] = None
    template_id: Optional[str] = None
    status: Optional[str] = None
    plan_activation_date: Optional[str] = None
    plan_expiration_date: Optional[str] = None

    def audit_payload(self) -> Dict[str, Any]:
        payload = super().audit_payload()
        payload.pop("password", None)
        return payload


def parse_form(schema_cls: type[FormModel], form: Any) -> tuple[Optional[FormModel], list[str]]:
    try:
        schema = schema_cls.from_form(form)
        return schema, []
    except ValidationError as exc:
        return None, [f"{error['loc'][0]}: {error['msg']}" for error in exc.errors()]
