from datetime import datetime, timedelta
from typing import List

from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from todayi.backend.base import Backend
from todayi.backend.filter import EntryFilterSettings
from todayi.model.entry import Entry
from todayi.model.tag import Tag


Base = declarative_base()


association_table = Table(
    "entries_tags_associations",
    Base.metadata,
    Column("entry_id", Integer, ForeignKey("entries.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class SqliteTag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    uuid = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    entries = relationship(
        "SqliteEntry", secondary=association_table, back_populates="tags"
    )


class SqliteEntry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    content = Column(String)
    uuid = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    tags = relationship(
        "SqliteTag", secondary=association_table, back_populates="entries"
    )


class SqliteBackend(Backend):

    _session = None

    def __init__(self, path_to_db: str):
        self._init_sqlite(path_to_db)
        self._session = self._create_session()

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
        reconciled_db_tags = self._reconcile_tags(tags)
        return [Tag(name=t.name, uuid=t.uuid) for t in reconciled_db_tags]

    def write_entry(self, entry: Entry):
        """
        Given an entry, write to db.
        """
        tags = entry.tags
        reconciled_db_tags = self._reconcile_tags(tags)
        dbentry = SqliteEntry(
            content=entry.content, uuid=entry.uuid, tags=reconciled_db_tags
        )
        self._session.add(dbentry)
        self._session.commit()

    def read_entries(
        self,
        entry_filter: EntryFilterSettings = EntryFilterSettings(
            after=datetime.now() - timedelta(days=2)
        ),
    ) -> List[Entry]:
        """
        Reads entries from backend with given filter settings.
        By default reads entries for past 48 hrs.

        :param filter:
        :type filter: EntryFilterSettings
        :return: List[Entry]
        """
        dbentries = self._read_entries(entry_filter)
        return [
            Entry(content=e.content, uuid=e.uuid, tags=e.tags, created_at=e.created_at)
            for e in dbentries
        ]

    def _create_session(self):
        return self.SqliteSession()

    def _init_sqlite(self, path_to_db: str):
        engine = create_engine("sqlite:///{}".format(path_to_db))
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.SqliteSession = Session

    def _reconcile_tags(self, tags: List[Tag]) -> List[SqliteTag]:
        """
        Given list of tags, reconcile those tags with db. If
        tag does not exist, add to db. If it does, return tag
        from db.

        :param tags: user created tags to resolve with backend
        :type tags: List[Tag]
        :return: List[SqliteTag]
        """
        result = []
        for tag in tags:
            dbtag = self._session.query(SqliteTag).filter_by(name=tag.name).first()
            if dbtag is None:
                dbtag = SqliteTag(name=tag.name, uuid=tag.uuid)
                self._session.add(dbtag)
                self._session.commit()
            result.append(dbtag)
        return result

    def _read_entries(self, entry_filter: EntryFilterSettings) -> List[SqliteEntry]:
        """
        Given filtering settings for entries, return
        matching records from sqlite

        :param entry_filter: settings for filtering
        :type entry_filter: EntryFilterSettings
        :return: List[SqliteEntry]
        """
        query = self._session.query(SqliteEntry)

        # Content filtering
        if entry_filter.content_contains is not None:
            query = query.filter(
                SqliteEntry.content.like("%{}%".format(entry_filter.content_contains))
            )
        if entry_filter.content_equals is not None:
            query = query.filter_by(content=entry_filter.content_equals)
        if entry_filter.content_not_contains:
            query = query.filter(
                SqliteEntry.content.notlike(
                    "%{}%".format(entry_filter.content_not_contains)
                )
            )
        if entry_filter.content_not_equals is not None:
            query = query.filter(
                SqliteEntry.content.isnot(entry_filter.content_not_equals)
            )

        # Date filtering
        if entry_filter.after is not None:
            query = query.filter(SqliteEntry.created_at >= entry_filter.after)
        if entry_filter.before is not None:
            query = query.filter(SqliteEntry.created_at <= entry_filter.before)

        # Tag filtering
        if entry_filter.with_tags is not None:
            resolved_tags = self._reconcile_tags(entry_filter.with_tags)
            query = query.filter(SqliteEntry.tags.in_(resolved_tags))
        if entry_filter.without_tags is not None:
            resolved_tags = self._reconcile_tags(entry_filter.without_tags)
            query = query.filter(~SqliteEntry.tags.in_(resolved_tags))

        return query.all()