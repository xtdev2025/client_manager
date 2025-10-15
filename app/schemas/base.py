from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Pydantic-compatible ObjectId wrapper."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.union_schema(
                [core_schema.is_instance_schema(ObjectId), core_schema.str_schema()]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: core_schema.CoreSchema, handler: Any) -> dict[str, Any]:
        json_schema = handler(schema)
        json_schema.update({"type": "string", "pattern": "^[0-9a-fA-F]{24}$"})
        return json_schema

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError("Invalid ObjectId")


class MongoDocumentSchema(BaseModel):
    """Base schema for MongoDB-backed documents."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        extra="allow",
    )

    @field_serializer("id", when_used="json")
    def serialize_id(self, value: Optional[PyObjectId]) -> Optional[str]:
        return str(value) if value else None

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_datetime(cls, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None

    def to_serializable_dict(self, *, exclude_none: bool = True) -> dict[str, Any]:
        """Return a JSON-friendly dict with Mongo aliases preserved."""
        return self.model_dump(by_alias=True, mode="json", exclude_none=exclude_none)


class MongoPayloadSchema(BaseModel):
    """Base class for payloads sent to Mongo-backed models."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

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


class MongoUpdateSchema(MongoPayloadSchema):
    """Base class for partial update payloads."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", populate_by_name=True)

    def to_update_dict(self) -> dict[str, Any]:
        """Dump only provided fields for update operations."""
        return self.model_dump(exclude_unset=True, exclude_none=True)
