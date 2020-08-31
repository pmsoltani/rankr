import csv
import io
from pathlib import Path
from typing import Dict, Iterator, Union


def get_row(
    file_path: Union[Path, str], encoding: str = "utf-8", delimiter: str = ","
) -> Iterator[Dict[str, str]]:
    """Yields a row from a .csv file

    This simple function is used to yield a .csv file in 'file_path',
    row-by-row, so as not to consume too much memory.

    Args:
        file_path (Path): the path to the .csv file
        encoding (str): encoding to be used when reading the .csv file
        delimiter (str): the delimiter used in the .csv file

    Yields:
        row: a row of the .csv file as a dictionary
    """
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            yield row
