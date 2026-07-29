from pydantic import BaseModel


class InstitutionBase(BaseModel):
    id: int | None = None
    country_id: int | None = None

    ror_id: str
    grid_id: str | None = None
    name: str
    established: int | None = None
    lat: str | None = None
    lng: str | None = None
    city: str | None = None
    state: str | None = None
    soup: str | None = None


class InstitutionCreate(InstitutionBase):
    country_id: int
