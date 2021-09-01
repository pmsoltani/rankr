from typing import List

from pydantic import BaseModel

from rankr.schemas.institution import InstitutionOut


class SearchResults(BaseModel):
    institutions: List[InstitutionOut]
