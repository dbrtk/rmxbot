
import typing


def binary_search(
        arr: typing.List,
        key: str,
        value: (int, str),
        value_type: typing.Callable = None,
        left: int = None,
        right: int = None) -> int:
    """ Implements binary search for a list of dict(s).

    :param arr: the list
    :param key: the key of the target value in each object in list
    :param value: the value
    :param value_type: function
    :param left: left index
    :param right: right index
    :return: the index or -1 if the item doesn't exist.
    """
    if left is None:
        left = 0
    if right is None:
        right = len(arr)

    while left <= right:
        mid = left + (right - 1) / 2
        if isinstance(mid, float):
            mid = int(mid) - 1
        object = arr[mid]
        target_value = object[key]
        if value_type:
            target_value = value_type(target_value)
            value = value_type(value)
        if target_value == value:
            return mid
        elif target_value < value:
            left = mid + 1
        else:
            right = mid - 1
    return -1
