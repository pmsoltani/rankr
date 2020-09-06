import io
from pathlib import Path
from typing import Union


def str_export(
    file_path: Union[Path, str], data: str, encoding: str = "utf-8",
) -> None:
    """Exports a string to the specified file.

    Args:
        file_path (Union[Path, str]): The path to the .csv file
        data (str): The data to be exported
        encoding (str, optional): The encoding to be used when writing
        the .csv file. Defaults to "utf-8".
    """
    with io.open(file_path, "w", encoding=encoding) as json_file:
        json_file.write(data)
