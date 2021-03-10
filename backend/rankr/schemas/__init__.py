"""pydantic models (schemas) to validate/filter data prior sending to client"""

# from rankr.schemas.entity import EntityBase
from rankr.schemas.ranking import RankingCreate
from rankr.schemas.acronym import AcronymCreate, AcronymDB, AcronymOut
from rankr.schemas.alias import AliasCreate, AliasDB, AliasOut
from rankr.schemas.country import CountryCreate, CountryDB, CountryOut
from rankr.schemas.institution import (
    InstitutionCreate,
    InstitutionDB,
    InstitutionOut,
)
from rankr.schemas.label import LabelCreate, LabelDB, LabelOut
from rankr.schemas.link import LinkCreate, LinkDB, LinkOut
