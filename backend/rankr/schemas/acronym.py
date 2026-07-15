from pydantic import BaseModel


class AcronymBase(BaseModel):
    id: int | None
    institution_id: int | None
    acronym: str | None


class AcronymCreate(AcronymBase):
    institution_id: int
