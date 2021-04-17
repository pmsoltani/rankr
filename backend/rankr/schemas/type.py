from typing import Optional

from pydantic import BaseModel

from config import enums as e
from rankr.schemas.core import OrmBase


class TypeBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    type: e.InstTypeEnum


class TypeCreate(TypeBase):
    institution_id: int


class TypeOut(TypeBase):
    pass


class TypeDB(OrmBase, TypeBase):
    pass
