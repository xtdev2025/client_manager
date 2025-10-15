from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import ValidationError, field_validator

from app.schemas.base import MongoPayloadSchema

FormModelT = TypeVar("FormModelT", bound="FormModel")


class FormModel(MongoPayloadSchema):
    """Base Pydantic model with helpers for parsing Flask request forms."""

    model_config = {
        "extra": "ignore",
        "str_strip_whitespace": True,
        "str_min_length": 0,
        "populate_by_name": True,
    }

    @field_validator("*", mode="before")
    @classmethod
    def _empty_string_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @classmethod
    def from_form(cls: Type[FormModelT], form: Any) -> FormModelT:
        raw_data: Dict[str, Any] = {}
        for field_name in cls.model_fields:
            if hasattr(form, "getlist"):
                values = form.getlist(field_name)
                if not values:
                    continue
                if len(values) > 1:
                    raw_data[field_name] = values
                    continue
                raw_value = values[0]
            else:
                if field_name not in getattr(form, "keys", lambda: [])():
                    continue
                raw_value = form.get(field_name)
            raw_data[field_name] = raw_value
        return cls.model_validate(raw_data)

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def audit_payload(self) -> Dict[str, Any]:
        return {
            key: value for key, value in self.model_dump().items() if value is not None
        }

    @staticmethod
    def normalize_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        value_str = str(value).strip().lower()
        return value_str in {"1", "true", "yes", "on"}


def parse_form(
    schema_cls: Type[FormModelT], form: Any
) -> tuple[Optional[FormModelT], list[str]]:
    try:
        schema = schema_cls.from_form(form)
        return schema, []
    except ValidationError as exc:
        return None, [f"{error['loc'][0]}: {error['msg']}" for error in exc.errors()]


class UpdateFormModel(FormModel):
    """Base class for update payloads received via forms."""

    model_config = {
        **FormModel.model_config,
        "extra": "ignore",
        "populate_by_name": True,
    }

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, exclude_unset=True)

    def audit_payload(self) -> Dict[str, Any]:
        return {
            key: value
            for key, value in self.model_dump(exclude_unset=True).items()
            if value is not None
        }
