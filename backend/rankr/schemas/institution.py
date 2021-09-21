from typing import List, Optional

from pydantic import BaseModel

from rankr.schemas.acronym import AcronymBase
from rankr.schemas.alias import AliasBase
from rankr.schemas.core import OrmBase
from rankr.schemas.country import CountryBase
from rankr.schemas.label import LabelBase
from rankr.schemas.link import LinkBase
from rankr.schemas.ranking import RankingDB
from rankr.schemas.type import TypeBase


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
    acronyms: List[AcronymBase] = []
    aliases: List[AliasBase] = []
    country: Optional[CountryBase]
    labels: List[LabelBase] = []
    links: List[LinkBase] = []
    rankings: List[RankingDB] = []
    types: List[TypeBase] = []

    ranks: List[RankingDB] = []
    stats: List[RankingDB] = []

    class Config:
        validate_assignment = True


class InstitutionDB(OrmBase, InstitutionOut):
    pass
