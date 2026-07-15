from typing import Optional

from pydantic import BaseModel

from config import enums as e


class TypeBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    type: e.InstTypeEnum


class TypeCreate(TypeBase):
    institution_id: int
