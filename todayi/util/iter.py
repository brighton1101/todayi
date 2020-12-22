"""
Module deals with iterables.
"""

from typing import Any


def is_iterable(obj: Any, allow_str: bool = False):
    """
    Given object `obj`, determine if it is an
    iterable collection. Note that by default,
    str objects are treated as not iterable,
    as they are not considered collections.

    :param obj: object under test
    :type obj: Any
    :param allow_str: allow str's (by default no)
    :type allow_str: bool
    """
    if isinstance(obj, str) and not allow_str:
        return False
    try:
        it = iter(obj)  # noqa
    except TypeError:
        return False
    return True
