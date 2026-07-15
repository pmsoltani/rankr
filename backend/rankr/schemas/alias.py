from typing import Optional

from pydantic import BaseModel


class AliasBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    alias: Optional[str]


class AliasCreate(AliasBase):
    institution_id: int
