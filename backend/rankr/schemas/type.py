from pydantic import BaseModel

from config import enums as e


class TypeBase(BaseModel):
    id: int | None = None
    institution_id: int | None = None
    type: e.InstTypeEnum


class TypeCreate(TypeBase):
    institution_id: int
