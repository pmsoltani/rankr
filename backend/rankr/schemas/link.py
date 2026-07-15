from pydantic import AnyHttpUrl, BaseModel, validator

from config import enums as e
from rankr.schemas.validators import basic_process


class LinkBase(BaseModel):
    id: int | None
    institution_id: int | None
    type: e.LinkTypeEnum = e.LinkTypeEnum.homepage
    link: AnyHttpUrl

    # validators
    _clean_link = validator("link", allow_reuse=True, pre=True)(basic_process)


class LinkCreate(LinkBase):
    institution_id: int
