from typing import Any, Dict, List


def group_by(items: List[Any], keys: List[str]) -> Dict[Any, List[Any]]:
    """Groups a list of dicts/objects by one or more keys/attrs.

    If the list of keys/attrs has more than one value, the keys of the
    output dictionary will be tuples of these values. For example:

    keys = ["year", "ranking_system"]
    result = {
        (2017, 'qs'): [items_group1],
        (2017, 'the'): [items_group2],
        (2018, 'qs'): [items_group3],
    }

    But if the list of keys/attrs has only one value, the result will
    be simpler:

    keys = ["year"]
    result = {
        2017: [items_group1],
        2017: [items_group2],
        2018: [items_group3],
    }

    Args:
        items (List[Any]): The list of items to be grouped
        keys (List[str]): The list of keys/attrs to perform the group by

    Returns:
        Dict[Any, List[Any]]: A dictionary containing grouped items.
    """
    result = {}
    for item in items:
        if isinstance(item, dict):
            keys_tuple = tuple(item[k] for k in keys)
        else:
            keys_tuple = tuple(getattr(item, k) for k in keys)

        keys_tuple = keys_tuple[0] if len(keys) == 1 else keys_tuple
        result.setdefault(keys_tuple, []).append(item)
    return result
