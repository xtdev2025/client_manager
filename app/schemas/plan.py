from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.schemas.forms import FormModel, UpdateFormModel

__all__ = ["PlanCreateSchema", "PlanUpdateSchema"]


class PlanCreateSchema(FormModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)


class PlanUpdateSchema(UpdateFormModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
