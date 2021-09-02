from typing import Dict, List

import typer
from pydantic import ValidationError
from tqdm.std import tqdm

from config import crwc
from rankr import db_models as d, repos as r, schemas as s
from utils import csv_size, get_csv, get_row, nullify


class GRIDCrawler:
    def __init__(
        self, country_repo: r.CountryRepo, institution_repo: r.InstitutionRepo
    ) -> None:
        self.country_repo = country_repo
        self.institution_repo = institution_repo

    def country_process(self) -> List[s.CountryDB]:
        typer.secho("Processing countries...", fg=typer.colors.CYAN)
        db_countries = self.country_repo.get_countries(limit=None)
        if not db_countries:
            rows = get_row(crwc.COUNTRIES_FILE)
            new_countries: Dict[str, s.CountryCreate] = {}
            for row in rows:
                nullify(row)
                country = s.CountryCreate(**row)
                new_countries[country.country] = country

            db_countries = self.country_repo.create_countries(
                list(new_countries.values())
            )
        return db_countries

    def institution_process(self):
        typer.secho("Processing institutions...", fg=typer.colors.CYAN)
        countries = {c.country: c for c in self.country_process()}
        rows = get_row(crwc.GRID_DATABASE_DIR / "institutes.csv")
        total_rows = csv_size(crwc.GRID_DATABASE_DIR / "institutes.csv")

        attrs = ["addresses", "acronyms", "aliases", "labels", "links", "types"]
        # Group the GRID data tables by grid_id for better access.
        institution_attrs = [
            get_csv(crwc.GRID_DATABASE_DIR / f"{attr}.csv", "grid_id")
            for attr in attrs
        ]

        db_institutions: List[d.Institution] = []
        for row in tqdm(rows, total=total_rows):
            nullify(row)
            if self.institution_repo.get_institution_by_grid_id(row["grid_id"]):
                continue

            # Get all the data related to the current institution.
            addresses, acronyms, aliases, labels, links, types = [
                attr.get(row["grid_id"], []) for attr in institution_attrs
            ]

            # Create 'soup' variable for fuzzy matching of institutions.
            soup = [row["name"]]

            try:
                raw_country = s.CountryCreate(
                    country=addresses[0].pop("country")
                )
                country = countries[raw_country.country]
                institution = s.InstitutionCreate(
                    **{**row, **addresses[0], "country_id": country.id}
                )
                soup.append(country.country)
            except IndexError:
                institution = s.InstitutionCreate(**row)

            soup.extend(i["acronym"] for i in acronyms)
            soup.extend(i["alias"] for i in aliases)
            soup.extend(i["label"] for i in labels)

            institution.soup = " | ".join(i for i in soup)
            db_institution = d.Institution(
                **institution.dict(exclude_unset=True)
            )

            acronyms = [d.Acronym(**i) for i in acronyms]
            aliases = [d.Alias(**i) for i in aliases]
            labels = [d.Label(**i) for i in labels]
            links = [d.Link(**i) for i in links]
            types = [d.Type(**i) for i in types]

            try:
                wikipedia_url = s.LinkCreate(
                    institution_id=0,
                    link=row["wikipedia_url"],
                    type="wikipedia",
                )
                wikipedia_url_dict = wikipedia_url.dict(exclude_unset=True)
                wikipedia_url_dict.pop("institution_id")
                links.append(d.Link(**wikipedia_url_dict))
            except ValidationError:
                pass

            db_institution.acronyms = acronyms  # type: ignore
            db_institution.aliases = aliases  # type: ignore
            db_institution.labels = labels  # type: ignore
            db_institution.links = links  # type: ignore
            db_institution.types = types  # type: ignore
            db_institutions.append(db_institution)

        typer.secho(
            "Committing results to the DB. This can take several minutes.",
            fg=typer.colors.CYAN,
        )
        self.institution_repo.create_db_institutions(db_institutions)

    def crawl(self):
        self.institution_process()
