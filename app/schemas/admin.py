from __future__ import annotations

from pydantic import Field, field_validator

from app.schemas.user import UserCreateSchema

__all__ = ["AdminCreateSchema"]


class AdminCreateSchema(UserCreateSchema):
    """Schema for admin creation validation."""

    role: str = Field(default="admin")

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in {"admin", "super_admin"}:
            raise ValueError("Role must be either admin or super_admin")
        return value
