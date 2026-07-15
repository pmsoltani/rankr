from typing import Optional

from pydantic import BaseModel, Field


class LabelBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    iso639: str = Field(..., regex=r"[a-z]{2}")
    label: Optional[str]


class LabelCreate(LabelBase):
    institution_id: int
