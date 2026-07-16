import json
from typing import Any, TypeVar

import typer
from pydantic import BaseModel, ValidationError
from tqdm import tqdm

from config import crwc
from rankr import db_models as d
from rankr import repos as r
from rankr import schemas as s
from utils import get_row, nullify


# ROR link types -> our link types.
_LINK_TYPES = {"website": "homepage", "wikipedia": "wikipedia"}

M = TypeVar("M", bound=d.Base)


def _build(
    model: type[M], schema: type[BaseModel], items: list[dict[str, Any]]
) -> list[M]:
    """Validate/clean each raw dict through its schema, then build ORM objects.

    Rows that fail validation (bad URL, missing iso639, ...) are skipped so a
    single malformed sub-record doesn't abort the whole institution.
    """
    objects: list[M] = []
    for item in items:
        try:
            objects.append(model(**schema(**item).model_dump(exclude_unset=True)))
        except ValidationError:
            continue
    return objects


class RORCrawler:
    """Populates the DB with institutions from the ROR data dump (v2 JSON)."""

    def __init__(
        self, country_repo: r.CountryRepo, institution_repo: r.InstitutionRepo
    ) -> None:
        self.country_repo = country_repo
        self.institution_repo = institution_repo

    def country_process(self) -> list[d.Country]:
        typer.secho("Processing countries...", fg=typer.colors.CYAN)
        db_countries = self.country_repo.get_countries(limit=None)
        if not db_countries:
            new_countries: dict[str, s.CountryCreate] = {}
            for row in get_row(crwc.COUNTRIES_FILE):
                nullify(row)
                country = s.CountryCreate(**row)
                new_countries[country.country] = country
            db_countries = self.country_repo.create_countries(
                list(new_countries.values())
            )
        return db_countries

    def _build_institution(
        self, record: dict[str, Any], countries: dict[str, d.Country]
    ) -> d.Institution | None:
        names = record.get("names", [])
        display = next((n["value"] for n in names if "ror_display" in n["types"]), None)
        if not display:
            return None

        ror_id = record["id"].rsplit("/", 1)[-1]
        if ror_id in crwc.EXCLUSIONS:
            return None

        grid_id = None
        for ext in record.get("external_ids", []):
            if ext["type"] == "grid":
                grid_id = ext.get("preferred") or next(iter(ext.get("all") or []), None)
                break

        location = (record.get("locations") or [{}])[0].get("geonames_details", {})
        country = countries.get(location.get("country_code"))

        acronyms = [n["value"] for n in names if "acronym" in n["types"]]
        aliases = [n["value"] for n in names if "alias" in n["types"]]
        labels = [n for n in names if "label" in n["types"]]

        soup = [display]
        if country:
            soup.append(country.country)
        soup.extend(acronyms)
        soup.extend(aliases)
        soup.extend(n["value"] for n in labels)

        lat, lng = location.get("lat"), location.get("lng")

        institution = s.InstitutionBase.model_validate(
            {
                "ror_id": ror_id,
                "grid_id": grid_id,
                "name": display,
                "established": record.get("established"),
                "lat": None if lat is None else str(lat),
                "lng": None if lng is None else str(lng),
                "city": location.get("name"),
                "state": location.get("country_subdivision_name"),
                "country_id": country.id if country else None,
            }
        )
        institution.soup = " | ".join(part for part in soup if part)

        db_institution = d.Institution(**institution.model_dump(exclude_unset=True))
        db_institution.acronyms = _build(
            d.Acronym, s.AcronymBase, [{"acronym": a} for a in acronyms]
        )
        db_institution.aliases = _build(
            d.Alias, s.AliasBase, [{"alias": a} for a in aliases]
        )
        db_institution.labels = _build(
            d.Label,
            s.LabelBase,
            [{"iso639": n.get("lang"), "label": n["value"]} for n in labels],
        )
        db_institution.types = _build(
            d.Type,
            s.TypeBase,
            [{"type": t.capitalize()} for t in record.get("types", [])],
        )
        db_institution.links = _build(
            d.Link,
            s.LinkBase,
            [
                {"type": _LINK_TYPES[lk["type"]], "link": lk.get("value")}
                for lk in record.get("links", [])
                if lk.get("type") in _LINK_TYPES
            ],
        )
        return db_institution

    def institution_process(self) -> None:
        countries = {c.country_code: c for c in self.country_process()}

        typer.secho(
            f"Loading ROR dump: {crwc.ROR_DATA_FILE.name}", fg=typer.colors.CYAN
        )
        with open(crwc.ROR_DATA_FILE, encoding="utf-8") as ror_file:
            records: list[dict[str, Any]] = json.load(ror_file)

        typer.secho(f"Processing {len(records)} institutions...", fg=typer.colors.CYAN)
        batch_size = 5000
        batch: list[d.Institution] = []
        for record in tqdm(records):
            institution = self._build_institution(record, countries)
            if institution is not None:
                batch.append(institution)
            if len(batch) >= batch_size:
                self.institution_repo.create_db_institutions(batch, log=False)
                batch = []
        if batch:
            self.institution_repo.create_db_institutions(batch, log=False)

    def crawl(self) -> None:
        self.institution_process()
