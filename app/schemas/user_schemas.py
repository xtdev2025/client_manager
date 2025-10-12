"""
Pydantic schemas for user validation.
"""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserCreateSchema(BaseModel):
    """Schema for user creation validation"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class AdminCreateSchema(UserCreateSchema):
    """Schema for admin creation validation"""

    role: str = Field(default="admin")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role"""
        if v not in ["admin", "super_admin"]:
            raise ValueError("Role must be either admin or super_admin")
        return v


class ClientCreateSchema(UserCreateSchema):
    """Schema for client creation validation"""

    plan_id: str = Field(..., min_length=24, max_length=24)
    template_id: Optional[str] = Field(None, min_length=24, max_length=24)
    status: str = Field(default="active")
    plan_activation_date: Optional[str] = None
    plan_expiration_date: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status"""
        if v not in ["active", "inactive"]:
            raise ValueError("Status must be either active or inactive")
        return v

    @field_validator("plan_id", "template_id")
    @classmethod
    def validate_object_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate MongoDB ObjectId format"""
        if v and len(v) != 24:
            raise ValueError("Invalid ObjectId format")
        return v


class UserUpdateSchema(BaseModel):
    """Schema for user update validation"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format"""
        if v:
            if not (v.replace('_', '').isalnum()):
                raise ValueError("Username must contain only alphanumeric characters and underscores")
            return v.lower()
        return None


class LoginSchema(BaseModel):
    """Schema for login validation"""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class PlanCreateSchema(BaseModel):
    """Schema for plan creation validation"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price is positive"""
        return round(v, 2)

    @field_validator("duration_days")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Validate duration is positive"""
        return v


class DomainCreateSchema(BaseModel):
    """Schema for domain creation validation"""

    domain: str = Field(..., min_length=3, max_length=255)
    cloudflare_email: Optional[str] = None
    cloudflare_api_key: Optional[str] = None
    ssl_enabled: bool = Field(default=False)
    max_domains: int = Field(default=1, ge=1)

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate domain format"""
        if "." not in v:
            raise ValueError("Invalid domain format")
        return v.lower()
