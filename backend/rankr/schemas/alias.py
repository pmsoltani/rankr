from pydantic import BaseModel


class AliasBase(BaseModel):
    id: int | None
    institution_id: int | None
    alias: str | None


class AliasCreate(AliasBase):
    institution_id: int
