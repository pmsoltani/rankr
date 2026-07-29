import csv
import json
from pathlib import Path

import typer

from config import crwc


def db_crosswalk(
    output: Path = typer.Argument(None),
):
    """Generates a grid_id,ror_id crosswalk CSV from the ROR data dump.

    Used to remap legacy GRID identifiers (e.g. the manual matches file) to ROR.
    """
    if output is None:
        output = crwc.ESSENTIALS_DIR / "grid_to_ror.csv"

    with open(crwc.ROR_DATA_FILE, encoding="utf-8") as ror_file:
        records = json.load(ror_file)

    pairs: list[tuple[str, str]] = []
    for record in records:
        ror_id = record["id"].rsplit("/", 1)[-1]
        for ext in record.get("external_ids", []):
            if ext["type"] == "grid":
                for grid_id in ext.get("all") or []:
                    pairs.append((grid_id.rsplit("/", 1)[-1], ror_id))

    with open(output, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["grid_id", "ror_id"])
        writer.writerows(sorted(pairs))

    typer.secho(
        f"Wrote {len(pairs)} grid->ror pairs to {output}", fg=typer.colors.GREEN
    )
