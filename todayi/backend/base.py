from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

from todayi.backend.filter import EntryFilterSettings
from todayi.model.entry import Entry
from todayi.model.tag import Tag


class Backend(ABC):
    @abstractmethod
    def reconcile_tags(self, tags: List[Tag]) -> List[Tag]:
        """
        Given a list of tags, resolve such that
        the following occurs. For each tag in
        tags, find whether or not that tag already
        exists in the backend.
            - If already exists, swap the tag in the
              input list with the one preexisting
              within the backend
            - If does not exist, write the new tags
              to the backend

        :param tags: user created tags to resolve with backend
        :type tags: List[Tag]
        :return: List[Tag] reconciled with backend
        """
        pass

    @abstractmethod
    def write_entry(self, entry: Entry):
        """
        Given an entry, write to db. Note that
        this method should reconcile tags provided
        with entry before inserting into backend.

        :param entry: the entry to write
        :type entry: str
        """
        pass

    @abstractmethod
    def read_entries(
        self,
        filter: EntryFilterSettings = EntryFilterSettings(
            after=datetime.now() - timedelta(days=2)
        ),
    ) -> List[Entry]:
        """
        Reads entries from backend with given filter settings.
        By default reads entries for past 48 hrs.

        :param filter:
        :type filter: EntryFilterSettings
        :return:
        """
        pass
