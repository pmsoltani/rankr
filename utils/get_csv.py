import csv
import io
from pathlib import Path
from typing import Dict, List


def get_csv(
    file_path: Path, key: str, encoding: str = "utf-8", delimiter: str = ","
) -> Dict[str, List[Dict[str, str]]]:
    output: Dict[str, List[Dict[str, str]]] = {}
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            value = row.pop(key)
            if value in output:
                output[value].append(dict(row))
            else:
                output[value] = [dict(row)]

    return output
