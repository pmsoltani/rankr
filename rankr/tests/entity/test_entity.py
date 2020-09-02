import re
from decimal import Decimal
from typing import List

from devtools import debug

from config import APPConfig
from rankr.db_models import Country, Institution, Ranking
from rankr.tests.utils import override_get_db


class TestEntity(object):
    def test_institution_profile_route(self, client):
        db = next(override_get_db())
        institution: Institution = db.query(Institution).first()
        grid_id = institution.grid_id
        assert re.match(APPConfig.GRID_ID_PATTERN, grid_id)
        response = client.get(f"/i/{grid_id}")
        assert response.status_code == 200
        assert response.json()["name"] == institution.name
        assert response.json()["entity"] == institution.grid_id
        debug(response.json())
        assert response.json()["ranks"]
        assert response.json()["scores"]
        assert response.json()["stats"]

    def test_geo_profile_route(self, client):
        db = next(override_get_db())
        country: Country = (
            db.query(Country)
            .join(Country.institutions)
            .join(Institution.rankings)
            .filter(
                Ranking.metric == "Overall Score",
                Ranking.ranking_system == "the",
                Ranking.year == 2020,
                Ranking.value.isnot(None),
            )
            .first()
        )
        rankings: List[Ranking] = (
            db.query(Ranking)
            .join(Ranking.institution)
            .join(Institution.country)
            .filter(
                Country.country_code == country.country_code,
                Ranking.metric == "Overall Score",
                Ranking.ranking_system == "the",
                Ranking.year == 2020,
            )
            .all()
        )
        values = [r.value for r in rankings if r.value]
        mean_score = Decimal(sum(values) / len(values))
        response = client.get(f"/geo/{country.country_code}")
        assert response.status_code == 200

        assert response.json()["entity"] == country.country_code
        assert response.json()["name"] == country.country
        assert response.json()["ranks"]
        assert response.json()["scores"]
        assert response.json()["stats"]
        debug(response.json()["scores"])
        for score_ranking in response.json()["scores"]:
            if not score_ranking["year"] == 2020:
                continue
            if not score_ranking["ranking_system"] == "the":
                continue
            # if not score_ranking["metric"] == "Overall Score":
            #     continue
            assert round(Decimal(score_ranking["value"]), 3) == mean_score
            break
