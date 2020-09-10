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
    """Reads a .csv file as a dictionary, grouped by the specified key.

    Args:
        file_path (Union[Path, str]): The path to the .csv file
        key (str): The csv field name to perform the group by
        encoding (str, optional): The encoding to be used when reading
        the .csv file. Defaults to "utf-8".
        delimiter (str, optional): The delimiter used in the .csv file.
        Defaults to ",".

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary of grouped items
    """
    output: Dict[str, List[Dict[str, str]]] = {}
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            value = row.pop(key)
            output.setdefault(value, []).append(dict(row))

    return output
