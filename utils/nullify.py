from typing import Sequence

nulls = ("", " ", "-", "#n/a", "n/a", "#N/A", "N/A", "\\")


def nullify(data: dict, nulls: Sequence[str] = nulls) -> None:
    """Changes the null-looking values in a dictionary to None.

    If an item in the input dictionary has a null-looking value,it will
    be changed (in-place) to None, so that the database can stay clean.

    Args:
        data (dict): the dictionary to be processed for its null values
        nulls (Sequence[str], optional): [description]. Defaults to nulls.
    """
    for key in data:
        if data[key] in nulls:
            data[key] = None
