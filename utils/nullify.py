def nullify(
    data: dict,
    null_types: tuple = ("", " ", "-", "#n/a", "n/a", "#N/A", "N/A", "\\"),
) -> None:
    """Changes the null-looking values in a dictionary to None

    The function receives a dictionary and looping through its items. If
    an item has a null-looking value (defined by the 'null_types'
    tuple), it will be changed (in-place) to None. This is so that the
    database receiving the values could stay clean.

    Args:
        data (dict): the dictionary to be processed for its null values
        null_types (tuple): a tuple of values that resemble null

    Returns:
        None
    """
    for key in data:
        if data[key] in null_types:
            data[key] = None
