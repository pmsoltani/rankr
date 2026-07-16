from pydantic import BaseModel


class AliasBase(BaseModel):
    id: int | None = None
    institution_id: int | None = None
    alias: str | None = None


class AliasCreate(AliasBase):
    institution_id: int
