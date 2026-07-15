from pydantic import BaseModel, Field


class LabelBase(BaseModel):
    id: int | None
    institution_id: int | None
    iso639: str = Field(..., regex=r"[a-z]{2}")
    label: str | None


class LabelCreate(LabelBase):
    institution_id: int
