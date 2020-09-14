from config import dbc


class TestRanking(object):
    def test_ranking_systems_route(self, client):
        response = client.get("/ranking/ranking_systems")
        assert response.status_code == 200
        assert list(response.json()) == list(dbc.RANKINGS["metrics"])

    def test_ranking_tables(self, client):
        response = client.get("/ranking/qs/2020")
        assert "qs" in response.json()
        assert len(response.json()["qs"]) == 10
