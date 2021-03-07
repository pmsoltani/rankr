from typing import Optional

from pydantic import BaseModel, Field

from rankr.schemas.core import OrmBase


class LabelBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    iso639: str = Field(..., regex=r"[a-z]{2}")
    label: Optional[str]


class LabelCreate(LabelBase):
    pass


class LabelOut(LabelBase):
    pass


class LabelDB(LabelBase, OrmBase):
    pass
