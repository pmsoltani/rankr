import csv
import io
from pathlib import Path


def csv_size(
    file_path: Path | str, encoding: str = "utf-8", delimiter: str = ","
) -> int:
    """Returns the number of rows in a .csv file.

    This function uses python's generators, so it's both fast and efficient.

    Args:
        file_path (Path): The path to the .csv file
        encoding (str): The encoding used when reading the file. Defaults to "utf-8".
        delimiter (str): The delimiter used in the .csv file. Defaults to ",".

    Returns:
        int: The number of rows in the .csv file
    """
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        return sum(1 for row in reader)
