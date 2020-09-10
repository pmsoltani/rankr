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


class TestDBModels(object):
    def test_acronym_repr(self, data):
        a: Acronym = data.query(Acronym).first()
        assert str(a) == a.acronym

    def test_alias_repr(self, data):
        a: Alias = data.query(Alias).first()
        assert str(a) == a.alias

    def test_country_repr(self, data):
        c = data.query(Country).first()
        assert str(c) == f"{c.country_code}: {c.country}"

    def test_institution_repr(self, data):
        i = data.query(Institution).first()
        assert str(i) == f"{i.id} - {i.grid_id}: {i.name}"

    def test_label_repr(self, data):
        l: Label = data.query(Label).first()
        assert str(l) == f"{l.iso639}: {l.label}"

    def test_link_repr(self, data):
        l: Link = data.query(Link).first()
        assert str(l) == f"{l.type.name}: {l.link}"

    def test_ranking_repr(self, data):
        r = data.query(Ranking).first()
        assert (
            str(r)
            == f"{r.ranking_system.name} ({r.year}) | "
            + f"{r.field} ({r.subject}) -> "
            + f"{r.metric.name}: {r.value}"
        )

    def test_type_repr(self, data):
        t: Type = data.query(Type).first()
        assert str(t) == t.type.name
