from typing import Any, Dict, List


def group_by(items: List[Any], keys: List[str]) -> Dict[Any, List[Any]]:
    result = {}
    for item in items:
        if isinstance(item, dict):
            keys_tuple = tuple(item[k] for k in keys)
        else:
            keys_tuple = tuple(getattr(item, k) for k in keys)

        keys_tuple = keys_tuple[0] if len(keys) == 1 else keys_tuple
        result.setdefault(keys_tuple, []).append(item)
    return result
