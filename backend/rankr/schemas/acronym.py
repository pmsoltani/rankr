from pydantic import BaseModel


class AcronymBase(BaseModel):
    id: int | None = None
    institution_id: int | None = None
    acronym: str | None = None


class AcronymCreate(AcronymBase):
    institution_id: int
