from pathlib import Path
from random import choice, choices, randrange
from typing import List, Optional, Union

from rankr.db_models import (
    Acronym,
    Alias,
    Country,
    Institution,
    Label,
    Link,
    Ranking,
    Type,
)
from rankr.enums import (
    MetricEnum,
    RankingSystemEnum,
    RankingTypeEnum,
    ValueTypeEnum,
)
from utils import get_row, nullify


def fill_countries(file_path: Union[Path, str]) -> List[Country]:
    rows = get_row(file_path)
    countries_list: List[Country] = []
    for row in rows:
        nullify(row)
        countries_list.append(Country(**row))
    return countries_list


def fake_institutions(n: int = 1):
    institutions: List[Institution] = []
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(n):
        first = randrange(10 ** 3, 10 ** 6)
        second = "".join(choices("0123456789abcdef", k=randrange(1, 3)))
        grid_id = f"grid.{first}.{second}"
        name_1 = "".join(choices(alphabet, k=randrange(5, 8)))
        name_2 = choice(["institution", "university"])
        name = f"{name_1} {name_2}".title()

        acronym = Acronym(acronym=name_1[0] + name_2[1])
        alias = Alias(alias=f"{name_2} of {name_2}")
        label = Label(iso639="en", label=name)
        link = Link(link=f"http://{name_1}-{name_2}.com", type="homepage")
        inst_type = Type(type="Education")

        institution = Institution(
            **{
                "country_id": randrange(1, 50),
                "grid_id": grid_id,
                "name": name,
                "established": randrange(1800, 2020),
            }
        )
        institution.acronyms = [acronym]
        institution.aliases = [alias]
        institution.labels = [label]
        institution.links = [link]
        institution.types = [inst_type]

        institutions.append(institution)

    return institutions


def fake_ranking(
    metric_type: str = "rank",
    ranking_system: Union[RankingSystemEnum, str] = None,
    year: Optional[int] = None,
) -> Ranking:
    if not ranking_system:
        ranking_system = choice(list(RankingSystemEnum))
    ranking_type = RankingTypeEnum["university ranking"]

    metric = MetricEnum["Rank"]
    value_type = ValueTypeEnum["integer"]
    value = choices([randrange(1, 1000), None], weights=[8, 2], k=1)[0]
    if metric_type == "score":
        metric = MetricEnum["Overall Score"]
        value_type = ValueTypeEnum["percent"]
        value = choices([randrange(1000) / 10, None], weights=[8, 2], k=1)[0]
    if metric_type == "stat":
        metric = MetricEnum["# Students per Staff"]
        value_type = ValueTypeEnum["decimal"]
        value = choices([randrange(100) / 10, None], weights=[8, 2], k=1)[0]
        ranking_system = RankingSystemEnum["the"]
    if not year:
        year = randrange(2004, 2022)

    return Ranking(
        **{
            "ranking_system": ranking_system,
            "ranking_type": ranking_type,
            "year": year,
            "field": "All",
            "subject": "All",
            "metric": metric,
            "value_type": value_type,
            "value": value,
        }
    )


def fake_rankings() -> List[Ranking]:
    rankings: List[Ranking] = [
        fake_ranking("rank", year=2015),
        fake_ranking("rank", ranking_system="shanghai"),
    ]
    for metric_type in ["rank", "score", "stat"]:
        for ranking_system in ["qs", "the"]:
            for year in range(2016, 2021):
                rankings.append(fake_ranking(metric_type, ranking_system, year))
    return rankings
