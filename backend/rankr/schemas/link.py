from typing import Optional

from pydantic import BaseModel

from config import enums as e
from rankr.schemas.core import OrmBase


class LinkBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    type: Optional[e.LinkTypeEnum]
    link: Optional[str]


class LinkCreate(LinkBase):
    pass


class LinkOut(LinkBase):
    pass


class LinkDB(LinkBase, OrmBase):
    pass
