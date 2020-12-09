from abc import ABC
from datetime import datetime
from typing import List
import uuid

from todayi.model.tag import Tag


class Entry:
    """
    Represents a single entry. Keeps
    a timestamp for when it was created, as well as a
    uuid. Note that the uuid should not be used a
    key in whatever backend is being used.

    :param content: entry's content, ie "Finished xyz"
    :type content: str
    :param uuid: randomly generated uuid, by default
                 uuid v4
    :type uuid: datetime
    :param tags: tags that entry is associated with
    :type tags: List
    :param created_at: when entry was created
    :type created_at: datetime
    """

    def __init__(
        self,
        content: str,
        uuid: str = str(uuid.uuid4()),
        tags: List[Tag] = [],
        created_at: datetime = datetime.now(),
    ):
        self.content = content
        self.uuid = uuid
        self.tags = tags
        self.created_at = created_at
