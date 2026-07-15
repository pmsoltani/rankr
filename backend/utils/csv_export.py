import csv
import io
from pathlib import Path


def csv_export(
    file_path: Path | str,
    data: list[dict[str, str]],
    encoding: str = "utf-8",
) -> None:
    """Exports a list of dictionaries to a .csv file.

    Args:
        file_path (Path | str): The path to the .csv file
        data (list[dict[str, str]]): The data to be exported
        encoding (str, optional): The encoding to be used when writing
        the .csv file. Defaults to "utf-8".
    """
    with io.open(file_path, "w", newline="", encoding=encoding) as csv_file:
        writer = csv.DictWriter(csv_file, data[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(data)
