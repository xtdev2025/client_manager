from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["LoginSchema"]


class LoginSchema(BaseModel):
    """Schema for login validation."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
