import csv
import io
from pathlib import Path
from typing import Dict, List, Union


def get_csv(
    file_path: Union[Path, str],
    key: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
) -> Dict[str, List[Dict[str, str]]]:
    output: Dict[str, List[Dict[str, str]]] = {}
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            value = row.pop(key)
            output.setdefault(value, []).append(dict(row))

    return output
