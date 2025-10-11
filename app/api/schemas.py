"""
API Response Schemas
Pydantic schemas for API responses and documentation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Base Response Schemas
class SuccessResponse(BaseModel):
    """Success response schema"""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    code: Optional[int] = Field(None, description="Error code")


class ValidationError(BaseModel):
    """Validation error schema"""
    error: str = Field(..., description="Validation error message")
    field: Optional[str] = Field(None, description="Field that failed validation")


# User-related Schemas
class UserSchema(BaseModel):
    """Base user schema"""
    id: str = Field(..., description="User ID", alias="_id")
    username: str = Field(..., description="Username")
    user_type: str = Field(..., description="User type (admin/client)")
    role: str = Field(..., description="User role")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")
    updated_at: datetime = Field(..., description="Last update timestamp", alias="updatedAt")
    
    class Config:
        populate_by_name = True


class ClientSchema(UserSchema):
    """Client schema"""
    plan_id: Optional[str] = Field(None, description="Associated plan ID")
    status: str = Field(..., description="Client status (active/inactive)")
    plan_activated_at: Optional[datetime] = Field(None, description="Plan activation date", alias="planActivatedAt")
    expired_at: Optional[datetime] = Field(None, description="Plan expiration date", alias="expiredAt")
    template_id: Optional[str] = Field(None, description="Associated template ID")
    
    class Config:
        populate_by_name = True


class AdminSchema(UserSchema):
    """Admin schema"""
    pass


class ClientListResponse(BaseModel):
    """Response schema for client list"""
    clients: List[ClientSchema] = Field(..., description="List of clients")
    total: int = Field(..., description="Total number of clients")


class AdminListResponse(BaseModel):
    """Response schema for admin list"""
    admins: List[AdminSchema] = Field(..., description="List of admins")
    total: int = Field(..., description="Total number of admins")


# Plan Schemas
class PlanSchema(BaseModel):
    """Plan schema"""
    id: str = Field(..., description="Plan ID", alias="_id")
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    price: float = Field(..., description="Plan price")
    duration_days: int = Field(..., description="Plan duration in days")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")
    updated_at: datetime = Field(..., description="Last update timestamp", alias="updatedAt")
    
    class Config:
        populate_by_name = True


class PlanListResponse(BaseModel):
    """Response schema for plan list"""
    plans: List[PlanSchema] = Field(..., description="List of plans")
    total: int = Field(..., description="Total number of plans")


# Domain Schemas
class DomainSchema(BaseModel):
    """Domain schema"""
    id: str = Field(..., description="Domain ID", alias="_id")
    domain: str = Field(..., description="Domain name")
    cloudflare_email: Optional[str] = Field(None, description="Cloudflare email")
    ssl_enabled: bool = Field(False, description="SSL enabled status")
    max_domains: int = Field(1, description="Maximum allowed subdomains")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")
    updated_at: datetime = Field(..., description="Last update timestamp", alias="updatedAt")
    
    class Config:
        populate_by_name = True


class DomainListResponse(BaseModel):
    """Response schema for domain list"""
    domains: List[DomainSchema] = Field(..., description="List of domains")
    total: int = Field(..., description="Total number of domains")


# Template Schemas
class TemplateSchema(BaseModel):
    """Template schema"""
    id: str = Field(..., description="Template ID", alias="_id")
    name: str = Field(..., description="Template name")
    html_content: Optional[str] = Field(None, description="HTML content")
    css_content: Optional[str] = Field(None, description="CSS content")
    js_content: Optional[str] = Field(None, description="JavaScript content")
    description: Optional[str] = Field(None, description="Template description")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")
    updated_at: datetime = Field(..., description="Last update timestamp", alias="updatedAt")
    
    class Config:
        populate_by_name = True


class TemplateListResponse(BaseModel):
    """Response schema for template list"""
    templates: List[TemplateSchema] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")


# Banking Info Schemas
class InfoSchema(BaseModel):
    """Banking information schema"""
    id: str = Field(..., description="Info ID", alias="_id")
    client_id: str = Field(..., description="Associated client ID")
    agencia: str = Field(..., description="Bank branch")
    conta: str = Field(..., description="Account number")
    saldo: float = Field(0.0, description="Account balance")
    status: str = Field(..., description="Info status")
    is_active: bool = Field(False, description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp", alias="createdAt")
    updated_at: datetime = Field(..., description="Last update timestamp", alias="updatedAt")
    
    class Config:
        populate_by_name = True


class InfoListResponse(BaseModel):
    """Response schema for info list"""
    infos: List[InfoSchema] = Field(..., description="List of banking information")
    total: int = Field(..., description="Total number of infos")


# Audit Log Schema
class AuditLogSchema(BaseModel):
    """Audit log schema"""
    id: str = Field(..., description="Log ID", alias="_id")
    action: str = Field(..., description="Action performed")
    user_id: Optional[str] = Field(None, description="User who performed the action")
    target_id: Optional[str] = Field(None, description="Target resource ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    ip_address: Optional[str] = Field(None, description="IP address")
    timestamp: datetime = Field(..., description="Action timestamp")
    
    class Config:
        populate_by_name = True


class AuditLogListResponse(BaseModel):
    """Response schema for audit log list"""
    logs: List[AuditLogSchema] = Field(..., description="List of audit logs")
    total: int = Field(..., description="Total number of logs")


# Login Schemas
class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class LoginResponse(BaseModel):
    """Login response schema"""
    message: str = Field(..., description="Login result message")
    redirect: Optional[str] = Field(None, description="Redirect URL")


# Dashboard Schemas
class DashboardStatsSchema(BaseModel):
    """Dashboard statistics schema"""
    client_count: Optional[int] = Field(None, description="Total number of clients")
    admin_count: Optional[int] = Field(None, description="Total number of admins")
    plan_count: Optional[int] = Field(None, description="Total number of plans")
    domain_count: Optional[int] = Field(None, description="Total number of domains")
    info_count: Optional[int] = Field(None, description="Total number of banking infos")
    template_count: Optional[int] = Field(None, description="Total number of templates")
    active_clients: Optional[int] = Field(None, description="Number of active clients")
    active_infos: Optional[int] = Field(None, description="Number of active infos")
