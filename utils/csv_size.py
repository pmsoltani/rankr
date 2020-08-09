import csv
import io
from pathlib import Path


def csv_size(
    file_path: Path, encoding: str = "utf-8", delimiter: str = ","
) -> int:
    """Returns the number of rows in a .csv file

    This function uses python's generators, so it's both fast and
    efficient.

    Args:
        file_path (Path): the path to the .csv file
        encoding (str): encoding to be used when reading the .csv file
        delimiter (str): the delimiter used in the .csv file

    Returns:
        int: The number of rows in the .csv file
    """
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        return sum(1 for row in reader)
