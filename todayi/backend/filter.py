from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from todayi.model.tag import Tag


@dataclass
class EntryFilterSettings:
    """
    Backend-agnostic configuration for filtering
    Entry queries.

    Available kwargs:

    :param content_contains: contains this string pattern
    :type content_contains: Optional[str]
    :param content_equals: matches this string pattern
    :type content_equals: Optional[str]
    :param content_not_contains: does not contain str pattern
    :type content_not_contains: Optional[str]
    :param content_not_equals: does not match str pattern
    :type content_not_equals: Optional[str]
    :param after: entries only after this date
    :type after: Optional[datetime]
    :param before: entries only before this date
    :type beofre: Optional[datetime]
    :param with_tags: tags that entries should be associated w/
    :type with_tags: Optional[List[Tag]]
    :param without_tags: tags what entries shouldn't be associated w/
    :type without_tags: Optional[List[Tag]]
    """

    """
    Available content filtering:
        - content contains string pattern
        - content equals string pattern
        - content does not contain string pattern
        - content does not equal string pattern
    """
    content_contains: Optional[str] = None
    content_equals: Optional[str] = None
    content_not_contains: Optional[str] = None
    content_not_equals: Optional[str] = None

    """
    Available date filtering:
        - entries before a datetime
        - entries after a datetime
    """
    after: Optional[datetime] = None
    before: Optional[datetime] = None

    """
    Available tag filtering:
        - entries with tags
        - entries without tags
    """
    with_tags: Optional[List[Tag]] = None
    without_tags: Optional[List[Tag]] = None
