from pydantic import BaseModel


class InstitutionBase(BaseModel):
    id: int | None
    country_id: int | None

    grid_id: str
    name: str
    established: int | None
    lat: str
    lng: str
    city: str
    state: str
    soup: str | None


class InstitutionCreate(InstitutionBase):
    country_id: int
