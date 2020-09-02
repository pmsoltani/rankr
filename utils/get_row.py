import csv
import io
from pathlib import Path
from typing import Dict, Iterator, Union


def get_row(
    file_path: Union[Path, str], encoding: str = "utf-8", delimiter: str = ","
) -> Iterator[Dict[str, str]]:
    """Yields a row from a .csv file.

    This simple function is used to yield the specified .csv file
    row-by-row, so as not to consume too much memory.

    Args:
        file_path (Union[Path, str]): The path to the .csv file
        encoding (str, optional): The encoding to be used when reading
        the .csv file. Defaults to "utf-8".
        delimiter (str, optional): The delimiter used in the .csv file.
        Defaults to ",".

    Yields:
        Iterator[Dict[str, str]]: A row of .csv file as a dictionary
    """
    with io.open(file_path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            yield row
