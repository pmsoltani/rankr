import re
from decimal import Decimal
from typing import List

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
        assert response.json()["ranks"]
        assert response.json()["scores"]
        assert response.json()["stats"]

    def test_grid_id_not_found(self, client):
        bad_grid_id = "grid.000000.ff"
        assert re.match(APPConfig.GRID_ID_PATTERN, bad_grid_id)
        response = client.get(f"/i/{bad_grid_id}")
        assert response.status_code == 404

    def test_geo_on_institution_profile(self, client):
        db = next(override_get_db())
        country: Country = db.query(Country).join(Country.institutions).first()
        response = client.get(f"/i/{country.country}")
        assert response.status_code == 404

    def test_institution_on_geo_profile(self, client):
        db = next(override_get_db())
        institution: Institution = db.query(Institution).first()
        grid_id = institution.grid_id
        assert re.match(APPConfig.GRID_ID_PATTERN, grid_id)
        response = client.get(f"/geo/{grid_id}")
        assert response.status_code == 404

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
        # testing for aggregation
        values = [r.value for r in rankings if r.value]
        mean_score = Decimal(sum(values) / len(values))
        response = client.get(f"/geo/{country.country_code}")
        assert response.status_code == 200
        assert response.json()["entity"] == country.country_code
        assert response.json()["name"] == country.country
        assert response.json()["ranks"]
        assert response.json()["scores"]
        assert response.json()["stats"]
        for score_ranking in response.json()["scores"]:
            if not score_ranking["year"] == 2020:
                continue
            if not score_ranking["ranking_system"] == "the":
                continue
            # if not score_ranking["metric"] == "Overall Score":
            #     continue
            assert round(Decimal(score_ranking["value"]), 3) == mean_score
            break

    def test_geo_not_found(self, client):
        entity = "world2"
        response = client.get(f"/geo/{entity}")
        assert response.status_code == 404

    def test_world_geo_profile_route(self, client):
        entity = "world"
        response = client.get(f"/geo/{entity}")
        assert response.status_code == 200

    def test_region_geo_profile_route(self, client):
        db = next(override_get_db())
        country: Country = db.query(Country).join(Country.institutions).first()
        entity = country.region
        response = client.get(f"/geo/{entity}")
        assert response.status_code == 200

    def test_sub_region_geo_profile_route(self, client):
        db = next(override_get_db())
        country: Country = db.query(Country).join(Country.institutions).first()
        entity = country.sub_region
        response = client.get(f"/geo/{entity}")
        assert response.status_code == 200

    def test_entity_compare_route(self, client):
        db = next(override_get_db())
        institution: Institution = db.query(Institution).first()
        grid_id = institution.grid_id
        country: Country = db.query(Country).join(Country.institutions).first()
        country_code = country.country_code

        response = client.get(f"/geo/{country_code}/compare?entities={grid_id}")
        assert response.status_code == 200
        assert response.json()[0]["entity"] == country_code
        assert response.json()[1][0]["entity"] == grid_id

    def test_entity_compare_institution_on_geo_route(self, client):
        db = next(override_get_db())
        institution: Institution = db.query(Institution).first()
        grid_id = institution.grid_id
        country: Country = db.query(Country).join(Country.institutions).first()
        country_code = country.country_code

        response = client.get(f"/geo/{grid_id}/compare?entities={country_code}")
        assert response.status_code == 404
