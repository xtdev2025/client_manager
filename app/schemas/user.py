from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

__all__ = ["UserCreateSchema", "UserUpdateSchema"]


class UserCreateSchema(BaseModel):
    """Schema for user creation validation."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.replace("_", "").isalnum():
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class UserUpdateSchema(BaseModel):
    """Schema for user update validation."""

    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: Optional[str]) -> Optional[str]:
        if value:
            if not value.replace("_", "").isalnum():
                raise ValueError(
                    "Username must contain only alphanumeric characters and underscores"
                )
            return value.lower()
        return None
