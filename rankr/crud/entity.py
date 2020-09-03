from typing import List, Optional

from fastapi import HTTPException
from furl import furl
from sqlalchemy.orm import Session

from config import appc
from rankr.db_models import Institution, Ranking, Country
from rankr.enums import (
    EntityTypeEnum,
    MetricEnum,
    RankingSystemEnum,
    RankingTypeEnum,
    StatMetricEnum,
)
from utils import group_by


class Entity(object):
    """For representing an entity, whether an institution or a geo entity"""

    def __init__(
        self,
        db: Session,
        entity: str,
        entity_type: EntityTypeEnum,
        name: Optional[str] = None,
        remove_nulls: bool = True,
    ) -> None:
        self.db = db
        self.entity = entity
        self.entity_type = entity_type
        self.remove_nulls = remove_nulls
        self.name = name
        self.ids: List[int] = []

        route_path = appc.ENTITIES["entity_types"][self.entity_type.name]
        self.url = (furl(appc.APP_TLD) / [route_path, self.entity]).url

        msg = f"'{self.entity}' of type '{self.entity_type.name}'"
        self.entity_404 = {
            "status_code": 404,
            "detail": f"Entity {msg} not found.",
        }

        self._ranks: List[Ranking] = []
        self._scores: List[Ranking] = []
        self._stats: List[Ranking] = []

    @property
    def profile(self) -> "Entity":
        if self.entity_type == EntityTypeEnum["institution"]:
            self.get_institution_data()
        self.ranks
        self.scores
        self.stats
        return self

    @property
    def ranks(self) -> List[Ranking]:
        if not self._ranks:
            ranks = self._get_metrics(metrics=[MetricEnum["Rank"]])
            self._ranks = self._aggregate_metrics(ranks)
        return self._ranks

    @property
    def scores(self) -> List[Ranking]:
        if not self._scores:
            score_metrics = [m for m in MetricEnum if "Score" in m.name]
            scores = self._get_metrics(metrics=score_metrics)
            self._scores = self._aggregate_metrics(scores)
        return self._scores

    @property
    def stats(self) -> List[Ranking]:
        if not self._stats:
            stat_metrics = [MetricEnum[stat.name] for stat in StatMetricEnum]
            stats = self._get_metrics(
                metrics=stat_metrics,
                ranking_system=RankingSystemEnum["the"],
                latest=True,
            )
            self._stats = self._aggregate_metrics(stats)
        return self._stats

    def get_institution_data(self) -> None:
        """Attaches institutional data to the entity"""
        institution: Institution = (
            self.db.query(Institution)
            .filter(Institution.id.in_(self.get_ids()))
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

        query = self.db.query(Institution.id).join(Institution.rankings)

        # if self.entity_type.name == "World": don't filter the query!
        geo_types = ["region", "sub_region", "country", "country_code"]
        if self.entity_type.name in geo_types:
            query = query.join(Institution.country).filter(
                getattr(Country, self.entity_type.name) == self.entity,
            )
        if self.entity_type.name == "institution":
            query = query.filter(Institution.grid_id == self.entity)

        self.ids = [iid[0] for iid in query.group_by(Institution.id).all()]
        if not self.ids:
            raise HTTPException(**self.entity_404)
        return self.ids

    def _get_metrics(
        self,
        metrics: List[MetricEnum],
        ranking_system: Optional[RankingSystemEnum] = None,
        ranking_type: RankingTypeEnum = RankingTypeEnum["university ranking"],
        field: str = "All",
        subject: str = "All",
        year: Optional[int] = None,
        latest: bool = False,
    ) -> List[Ranking]:
        """Retrieves ranking metrics for the institutions of the entity.

        Args:
            metrics (List[MetricEnum]): The list of desired metrics
            ranking_system (Optional[RankingSystemEnum], optional): The
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
            Ranking.institution_id.in_(self.get_ids()),
            Ranking.ranking_type == ranking_type,
            Ranking.field == field,
            Ranking.subject == subject,
            Ranking.metric.in_(metric.name for metric in metrics),
        )
        if ranking_system:
            filters = (*filters, Ranking.ranking_system == ranking_system)
        if latest:  # Get the latest year.
            year = (
                self.db.query(Ranking.year)
                .filter(*filters)
                .order_by(Ranking.year.desc())
                .limit(1)
            )
        filters = (*filters, Ranking.year == year) if year else filters
        query = self.db.query(Ranking).filter(*filters)

        ranking_metrics: List[Ranking] = query.order_by(Ranking.year).all()
        for metric in ranking_metrics:
            # enrich the Ranking objects with entity data
            metric.entity = self.entity
            metric.entity_type = self.entity_type

        return ranking_metrics

    def _aggregate_metrics(self, metrics: List[Ranking]) -> List[Ranking]:
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
        if self.entity_type == EntityTypeEnum["institution"]:
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

    def _create_metric(self, **kwargs) -> Ranking:
        """Creates a Ranking object using the specified kwargs.

        Returns:
            Ranking: The Ranking object
        """
        metric = Ranking(**{**self.__dict__, **kwargs})
        metric.entity = self.entity
        metric.entity_type = self.entity_type
        return metric
