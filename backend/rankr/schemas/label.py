from pydantic import BaseModel, Field


class LabelBase(BaseModel):
    id: int | None = None
    institution_id: int | None = None
    iso639: str = Field(..., pattern=r"[a-z]{2}")
    label: str | None = None


class LabelCreate(LabelBase):
    institution_id: int
