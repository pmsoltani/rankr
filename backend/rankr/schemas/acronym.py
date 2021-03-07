from typing import Optional

from pydantic import BaseModel

from rankr.schemas.core import OrmBase


class AcronymBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    acronym: Optional[str]


class AcronymCreate(AcronymBase):
    pass


class AcronymOut(AcronymBase):
    pass


class AcronymDB(AcronymBase, OrmBase):
    pass
