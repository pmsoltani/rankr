import csv
import io
from pathlib import Path
from typing import Dict, List, Union


def csv_export(
    file_path: Union[Path, str],
    data: List[Dict[str, str]],
    encoding: str = "utf-8",
):
    with io.open(file_path, "w", newline="", encoding=encoding) as csv_file:
        writer = csv.DictWriter(csv_file, data[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(data)
