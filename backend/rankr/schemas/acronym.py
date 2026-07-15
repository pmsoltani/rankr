from typing import Optional

from pydantic import BaseModel


class AcronymBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    acronym: Optional[str]


class AcronymCreate(AcronymBase):
    institution_id: int
