from pydantic import BaseModel

from config import enums as e


class TypeBase(BaseModel):
    id: int | None
    institution_id: int | None
    type: e.InstTypeEnum


class TypeCreate(TypeBase):
    institution_id: int
