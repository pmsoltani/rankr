from typing import Optional

from pydantic import BaseModel

from rankr.schemas.core import OrmBase


class InstitutionBase(BaseModel):
    id: Optional[int]
    country_id: Optional[int]

    grid_id: str
    name: str
    established: Optional[int]
    lat: str
    lng: str
    city: str
    state: str
    soup: Optional[str]


class InstitutionCreate(InstitutionBase):
    country_id: int


class InstitutionOut(InstitutionBase):
    pass


class InstitutionDB(OrmBase, InstitutionBase):
    pass
