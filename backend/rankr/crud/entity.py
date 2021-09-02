from typing import List, Optional

from fastapi import HTTPException
from furl import furl
from sqlalchemy.orm import Session

from config import appc, enums as e
from rankr import db_models as d
from rankr import schemas as s
from utils import get_json, group_by, str_export


class Entity(object):
    """For representing an entity, whether an institution or a geo entity"""

    def __init__(
        self,
        db: Session,
        entity: str,
        entity_type: e.EntityTypeEnum,
        name: Optional[str] = None,
        remove_nulls: bool = True,
        fresh: bool = False,
    ) -> None:
        self.db = db
        self.entity = entity
        self.entity_type = entity_type
        self.remove_nulls = remove_nulls
        self.fresh = fresh
        self.name = name
        self.ids: List[int] = []

        route_path = appc.ENTITIES["entity_types"][self.entity_type.name]
        self.url = (furl(appc.APP_TLD) / [route_path, self.entity]).url

        msg = f"'{self.entity}' of type '{self.entity_type.name}'"
        self.entity_404 = {
            "status_code": 404,
            "detail": f"Entity {msg} not found.",
        }

        self.json_file_path = appc.RESPONSES_DIR / f"{self.entity}.json"
        self.json_file_path.parent.mkdir(parents=True, exist_ok=True)

        self._ranks: List[s.Ranking] = []
        self._scores: List[s.Ranking] = []
        self._stats: List[s.Ranking] = []

    @property
    def profile(self) -> "Entity":
        if not self.fresh and self.json_file_path.exists():
            return get_json(self.json_file_path)

        self.ranks
        self.scores
        self.stats
        if self.entity_type == e.EntityTypeEnum["institution"]:
            self.get_institution_data()
        if self.entity_type != e.EntityTypeEnum["institution"]:
            data = {k: v for k, v in self.__dict__.items()}
            for attr in ["ranks", "scores", "stats"]:
                data[attr] = data.pop(f"_{attr}")

            str_export(self.json_file_path, s.EntitySchema(**data).json())
        return self

    @property
    def ranks(self) -> List[s.Ranking]:
        if not self._ranks:
            ranks = self._get_metrics(metrics=[e.MetricEnum["Rank"]])
            self._ranks = self._aggregate_metrics(ranks)
        return self._ranks

    @property
    def scores(self) -> List[s.Ranking]:
        if not self._scores:
            score_metrics = [m for m in e.MetricEnum if "Score" in m.name]
            scores = self._get_metrics(metrics=score_metrics)
            self._scores = self._aggregate_metrics(scores)
        return self._scores

    @property
    def stats(self) -> List[s.Ranking]:
        if not self._stats:
            stat_metrics = [
                e.MetricEnum[stat.name] for stat in e.StatMetricEnum
            ]
            stats = self._get_metrics(
                metrics=stat_metrics,
                ranking_system=e.RankingSystemEnum["the"],
                latest=True,
            )
            self._stats = self._aggregate_metrics(stats)
        return self._stats

    def get_institution_data(self) -> None:
        """Attaches institutional data to the entity"""
        institution: Optional[d.Institution] = (
            self.db.query(d.Institution)
            .filter(d.Institution.id.in_(self.get_ids()))
            .first()
        )
        attrs = ["name", "wikipedia_url", "established", "lat", "lng", "city"]
        for attr in attrs:
            setattr(self, attr, getattr(institution, attr))
        self.country = institution.country.country
        self.country_code = institution.country.country_code

    def get_ids(self) -> List[int]:
        """Retrieves the institution ID(s) for an entity"""
        if self.ids:
            return self.ids

        query = self.db.query(d.Institution.id).join(d.Institution.rankings)

        # if self.entity_type.name == "World": don't filter the query!
        geo_types = ["region", "sub_region", "country", "country_code"]
        if self.entity_type.name in geo_types:
            query = query.join(d.Institution.country).filter(
                getattr(d.Country, self.entity_type.name) == self.entity,
            )
        if self.entity_type.name == "institution":
            query = query.filter(d.Institution.grid_id == self.entity)

        self.ids = [iid[0] for iid in query.group_by(d.Institution.id).all()]
        if not self.ids:
            raise HTTPException(**self.entity_404)
        return self.ids

    def _get_metrics(
        self,
        metrics: List[e.MetricEnum],
        ranking_system: Optional[e.RankingSystemEnum] = None,
        ranking_type: e.RankingTypeEnum = e.RankingTypeEnum[
            "university ranking"
        ],
        field: str = "All",
        subject: str = "All",
        year: Optional[int] = None,
        latest: bool = False,
    ) -> List[s.Ranking]:
        """Retrieves ranking metrics for the institutions of the entity.

        Args:
            metrics (List[MetricEnum]): The list of desired metrics
            ranking_system (Optional[e.RankingSystemEnum], optional): The
            ranking system to query on. If not specified, will query
            all ranking systems. Defaults to None.
            ranking_type (RankingTypeEnum, optional): The ranking type.
            Defaults to RankingTypeEnum["university ranking"].
            field (str, optional): The ranking field. Defaults to "All".
            subject (str, optional): The ranking subject. Defaults to
            "All".
            year (Optional[int], optional): The ranking year. If not
            specified, will query all years. Defaults to None.
            latest (bool, optional): If True, will return the results
            for the latest year. Defaults to False.

        Returns:
            List[Ranking]: A list of Ranking objects
        """
        # building the query
        filters = (
            d.Ranking.institution_id.in_(self.get_ids()),
            d.Ranking.ranking_type == ranking_type,
            d.Ranking.field == field,
            d.Ranking.subject == subject,
            d.Ranking.metric.in_(metric.name for metric in metrics),
        )
        if ranking_system:
            filters = (*filters, d.Ranking.ranking_system == ranking_system)
        if latest:  # Get the latest year.
            year = (
                self.db.query(d.Ranking.year)
                .filter(*filters)
                .order_by(d.Ranking.year.desc())
                .limit(1)
            )
        filters = (*filters, d.Ranking.year == year) if year else filters
        query = self.db.query(d.Ranking).filter(*filters)

        ranking_metrics: List[d.Ranking] = query.order_by(d.Ranking.year).all()
        for metric in ranking_metrics:
            # enrich the Ranking objects with entity data
            metric.entity = self.entity
            metric.entity_type = self.entity_type

        return ranking_metrics

    def _aggregate_metrics(self, metrics: List[s.Ranking]) -> List[s.Ranking]:
        """Aggregates the metric values for different institutions.

        The function attempts to group a list of rankings by year,
        ranking system, and metric type. In each group, it will then
        calculates the mean value and assigns the result to a new
        Ranking object, which is in turn appended to the results list.

        Args:
            metrics (List[Ranking]): The list of ranking metrics to be
            aggregated

        Returns:
            List[Ranking]: The list of aggregated metrics
        """
        if self.entity_type == e.EntityTypeEnum["institution"]:
            return metrics

        fields = ["year", "ranking_system", "metric"]
        grouped_metrics = group_by(metrics, fields)
        result = []
        for group, metrics_in_group in grouped_metrics.items():
            values = [m.value for m in metrics_in_group if m.value]
            if not values:
                continue

            count = len(values) if self.remove_nulls else len(self.ids)
            mean = round(sum(values) / count, 2)

            kwargs = {
                **metrics_in_group[0].__dict__,
                **dict(zip(fields, group)),
                "value": mean,
            }
            aggregated_metric = self._create_metric(**kwargs)
            result.append(aggregated_metric)

        return result

    def _create_metric(self, **kwargs) -> s.Ranking:
        """Creates a Ranking object using the specified kwargs.

        Returns:
            Ranking: The Ranking object
        """
        metric = s.Ranking(**{**self.__dict__, **kwargs})
        metric.entity = self.entity
        metric.entity_type = self.entity_type
        return metric
