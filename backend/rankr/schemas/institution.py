from typing import Optional

from pydantic import BaseModel

from rankr.schemas.core import OrmBase


class InstitutionBase(BaseModel):
    id: Optional[int]
    country_id: Optional[int]

    grid_id: str
    name: str
    wikipedia_url: str
    established: int
    lat: str
    lng: str
    city: str
    state: str
    soup: str


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionOut(InstitutionBase):
    pass


class InstitutionDB(InstitutionBase, OrmBase):
    pass
