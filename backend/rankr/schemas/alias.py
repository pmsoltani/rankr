from typing import Optional

from pydantic import BaseModel

from rankr.schemas.core import OrmBase


class AliasBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]
    alias: Optional[str]


class AliasCreate(AliasBase):
    pass


class AliasOut(AliasBase):
    pass


class AliasDB(AliasBase, OrmBase):
    pass
