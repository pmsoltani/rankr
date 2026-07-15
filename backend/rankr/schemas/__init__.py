"""pydantic models (schemas) to validate & clean crawled data before writing."""

from rankr.schemas.acronym import AcronymBase, AcronymCreate
from rankr.schemas.alias import AliasBase, AliasCreate
from rankr.schemas.country import CountryCreate
from rankr.schemas.institution import InstitutionCreate
from rankr.schemas.label import LabelBase, LabelCreate
from rankr.schemas.link import LinkCreate
from rankr.schemas.ranking import RankingCreate
from rankr.schemas.type import TypeBase, TypeCreate
