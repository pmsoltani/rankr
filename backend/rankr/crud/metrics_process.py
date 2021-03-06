from typing import Dict, List

from config import dbc
from rankr.db_models import Ranking
from utils import value_process


metric_types = dbc.RANKINGS["metrics"]
non_metric_cols = dbc.RANKINGS["non_metrics"]


def metrics_process(row: Dict[str, str]) -> List[Ranking]:
    """Converts a .csv row into a list of Ranking objects.

    Args:
        row (dict): The .csv row as a dictionary.

    Returns:
        List[Ranking]: The list of Ranking objects to be attached to an
        institution object.
    """
    ranking_system = row["Ranking System"]
    metrics = []
    for col in row:
        if col.lower() in non_metric_cols:
            continue

        metric = metric_types[ranking_system][col]["name"]
        value_type = metric_types[ranking_system][col]["type"]
        metric_value = value_process(row[col], value_type=value_type)
        metrics.append(
            Ranking(
                metric=metric,
                value=metric_value,
                value_type=value_type,
                ranking_system=ranking_system,
                ranking_type=row["Ranking Type"],
                year=row["Year"],
                field=row["Field"],
                subject=row["Subject"],
            )
        )
    return metrics
