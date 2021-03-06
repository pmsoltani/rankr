import enum

from config.app_config import APPConfig
from config.db_config import DBConfig


appc = APPConfig()
dbc = DBConfig()


# The Enums below are used to regulate & restrict the types of different things:
# institution types: Education, Company, ...
institution_types = appc.ENTITIES["institution_types"]
InstTypeEnum = enum.Enum("InstTypeEnum", {t: t for t in institution_types})

# institution link types: homepage, qs, ...
link_types = ["homepage"] + list(dbc.RANKINGS["metrics"])
LinkTypeEnum = enum.Enum("LinkTypeEnum", {t: t for t in link_types},)

# ranking system types: qs, shanghai, ...
RankingSystemEnum = enum.Enum(
    "RankingSystemEnum", {t: t for t in dbc.RANKINGS["metrics"]},
)

# ranking types: university ranking, subject ranking
RankingTypeEnum = enum.Enum(
    "RankingTypeEnum", {t: t for t in dbc.RANKINGS["ranking_types"]},
)

metric_types = []
metric_value_types = []
for metrics in dbc.RANKINGS["metrics"].values():
    for metric_info in metrics.values():
        metric_types.append(metric_info["name"])
        metric_value_types.append(metric_info["type"])

# metric types: Rank, Overall Score, ...
MetricEnum = enum.Enum("MetricEnum", {t: t for t in metric_types})

# statistic metric types: # FTE Students, % International Students, ...
StatMetricEnum = enum.Enum(
    "StatMetricEnum", {t: t for t in dbc.RANKINGS["stat_metrics"]}
)

# metric value types: integer, decimal, ...
ValueTypeEnum = enum.Enum("ValueTypeEnum", {t: t for t in metric_value_types})

# compare entity types (for comparing an institution with different entities)
entities = appc.ENTITIES["entity_types"]
EntityTypeEnum = enum.Enum("EntityTypeEnum", {t: t for t in entities})

# different paths for different entity_types: i, geo
EntityTypePathEnum = enum.Enum(
    "EntityTypePathEnum", {t: t for t in entities.values()}
)
