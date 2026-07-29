from pydantic import AnyHttpUrl, BaseModel, TypeAdapter, field_validator

from config import enums as e
from rankr.schemas.validators import basic_process


_url_adapter = TypeAdapter(AnyHttpUrl)


class LinkBase(BaseModel):
    id: int | None = None
    institution_id: int | None = None
    type: e.LinkTypeEnum = e.LinkTypeEnum.homepage
    link: str

    @field_validator("link", mode="before")
    @classmethod
    def _clean_and_validate_link(cls, value):
        # Clean, then validate URL shape via AnyHttpUrl (raises on bad input),
        # but keep the original string (v2 AnyHttpUrl would normalize it and is
        # not a str, which the SQLAlchemy String column can't store).
        value = basic_process(value)
        _url_adapter.validate_python(value)
        return value


class LinkCreate(LinkBase):
    institution_id: int
