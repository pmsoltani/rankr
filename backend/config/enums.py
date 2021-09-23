import enum

from config.crawler_config import CrawlerConfig


crwc = CrawlerConfig()


# The Enums below are used to regulate & restrict the types of different things:
# institution types: Education, Company, ...
institution_types = [
    "Archive",
    "Company",
    "Education",
    "Facility",
    "Government",
    "Healthcare",
    "Nonprofit",
    "Other",
]
InstTypeEnum = enum.Enum("InstTypeEnum", {t: t for t in institution_types})

# institution link types: homepage, qs, ...
link_types = ["homepage", "wikipedia"] + list(crwc.RANKINGS["metrics"])
LinkTypeEnum = enum.Enum("LinkTypeEnum", {t: t for t in link_types},)

# ranking system types: qs, shanghai, ...
RankingSystemEnum = enum.Enum(
    "RankingSystemEnum", {t: t for t in crwc.RANKINGS["metrics"]},
)

# ranking types: university ranking, subject ranking
RankingTypeEnum = enum.Enum(
    "RankingTypeEnum", {t: t for t in crwc.RANKINGS["ranking_types"]},
)

metric_types = []
metric_value_types = []
for metrics in crwc.RANKINGS["metrics"].values():
    for metric_info in metrics.values():
        metric_types.append(metric_info["name"])
        metric_value_types.append(metric_info["type"])

# metric types: Rank, Overall Score, ...
MetricEnum = enum.Enum("MetricEnum", {t: t for t in metric_types})

# statistic metric types: # FTE Students, % International Students, ...
StatMetricEnum = enum.Enum(
    "StatMetricEnum", {t: t for t in crwc.RANKINGS["stat_metrics"]}
)

# metric value types: integer, decimal, ...
ValueTypeEnum = enum.Enum("ValueTypeEnum", {t: t for t in metric_value_types})
