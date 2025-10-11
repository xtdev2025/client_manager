"""
Validation utilities using Pydantic schemas.
"""
from typing import Tuple, Optional, Dict, Any
from pydantic import ValidationError
from app.schemas.user_schemas import (
    UserCreateSchema,
    AdminCreateSchema,
    ClientCreateSchema,
    LoginSchema,
    PlanCreateSchema,
    DomainCreateSchema
)


def validate_user_create(
    data: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate user creation data.

    Args:
        data: Dict containing user data

    Returns:
        Tuple containing (is_valid, validated_data, error_message)
    """
    try:
        validated = UserCreateSchema(**data)
        return True, validated.model_dump(), None
    except ValidationError as e:
        errors = e.errors()
        error_msg = '; '.join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        return False, None, error_msg


def validate_admin_create(
    data: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate admin creation data.

    Args:
        data: Dict containing admin data

    Returns:
        Tuple containing (is_valid, validated_data, error_message)
    """
    try:
        validated = AdminCreateSchema(**data)
        return True, validated.model_dump(), None
    except ValidationError as e:
        errors = e.errors()
        error_msg = '; '.join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        return False, None, error_msg


def validate_client_create(
    data: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate client creation data.

    Args:
        data: Dict containing client data

    Returns:
        Tuple containing (is_valid, validated_data, error_message)
    """
    try:
        validated = ClientCreateSchema(**data)
        return True, validated.model_dump(), None
    except ValidationError as e:
        errors = e.errors()
        error_msg = '; '.join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        return False, None, error_msg


def validate_login(data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate login data.

    Args:
        data: Dict containing login credentials

    Returns:
        Tuple containing (is_valid, validated_data, error_message)
    """
    try:
        validated = LoginSchema(**data)
        return True, validated.model_dump(), None
    except ValidationError as e:
        errors = e.errors()
        error_msg = '; '.join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        return False, None, error_msg


def validate_plan_create(
    data: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate plan creation data.

    Args:
        data: Dict containing plan data

    Returns:
        Tuple containing (is_valid, validated_data, error_message)
    """
    try:
        validated = PlanCreateSchema(**data)
        return True, validated.model_dump(), None
    except ValidationError as e:
        errors = e.errors()
        error_msg = '; '.join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        return False, None, error_msg


def validate_domain_create(
    data: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate domain creation data.

    Args:
        data: Dict containing domain data

    Returns:
        Tuple containing (is_valid, validated_data, error_message)
    """
    try:
        validated = DomainCreateSchema(**data)
        return True, validated.model_dump(), None
    except ValidationError as e:
        errors = e.errors()
        error_msg = '; '.join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        return False, None, error_msg
