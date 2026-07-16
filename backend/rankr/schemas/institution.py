from pydantic import BaseModel


class InstitutionBase(BaseModel):
    id: int | None = None
    country_id: int | None = None

    grid_id: str
    name: str
    established: int | None = None
    lat: str
    lng: str
    city: str
    state: str
    soup: str | None = None


class InstitutionCreate(InstitutionBase):
    country_id: int
