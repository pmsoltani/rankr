import io
import json
from pathlib import Path
from typing import Callable, Union


def get_json(file_path: Union[Path, str], object_hook: Callable = None):
    """Reads a .json file.

    Args:
        file_path (Union[Path, str]): The path to the .json file
        object_hook (Callable, optional): A function to process values.
        Defaults to None.

    Returns:
        The contents of the .json file
    """
    with io.open(file_path, "r", encoding="utf-8") as json_file:
        return json.loads(json_file.read(), object_hook=object_hook)
