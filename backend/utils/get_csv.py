import csv
import io
from pathlib import Path


def get_csv(
    file_path: Path | str,
    key: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
) -> dict[str, list[dict[str, str]]]:
    """Reads a .csv file as a dictionary, grouped by the specified key.

    Args:
        file_path (Path | str): The path to the .csv file
        key (str): The csv field name to perform the group by
        encoding (str, optional): The encoding to be used when reading
        the .csv file. Defaults to "utf-8".
        delimiter (str, optional): The delimiter used in the .csv file.
        Defaults to ",".

    Returns:
        dict[str, list[dict[str, str]]]: A dictionary of grouped items
    """
    output: dict[str, list[dict[str, str]]] = {}
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            value = row.pop(key)
            output.setdefault(value, []).append(dict(row))

    return output
