from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, validator

from config import enums as e
from rankr.schemas.core import OrmBase
from rankr.schemas.validators import basic_process


class LinkBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    type: e.LinkTypeEnum
    link: AnyHttpUrl

    # validators
    _clean_link = validator("link", allow_reuse=True, pre=True)(basic_process)


class LinkCreate(LinkBase):
    pass


class LinkOut(LinkBase):
    pass


class LinkDB(LinkBase, OrmBase):
    pass
