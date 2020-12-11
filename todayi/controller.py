from datetime import datetime, timedelta
from typing import List

from todayi.backend.base import Backend
from todayi.backend.filter import EntryFilterSettings
from todayi.backend.sqlite import SqliteBackend
from todayi.config import (
    get as get_config,
    set as set_config,
    MissingConfigError,
    InvalidConfigError,
)
from todayi.frontend.terminal import TerminalFrontend
from todayi.model.entry import Entry
from todayi.model.tag import Tag
from todayi.util.fs import path


class Controller:

    _filter_kwargs = [
        'content_contains',
        'content_equals',
        'content_not_contains',
        'content_not_equals',
        'after',
        'before',
        'with_tags',
        'without_tags'
    ]

    def __init__(self):
        self._cached_backend = None
        self._filter_kwargs = set(self._filter_kwargs)

    @property
    def _backend(self) -> Backend:
        if self._cached_backend == None:
            self._init_backend()
        return self._cached_backend

    def write_entry(self, content: str, tags: List[str] = []):
        """
        Given users' input content and a list of tags,
        write entry to backend.

        :param content: entry's content
        :type content: str
        :param tags: optional list of tags to associate
                     entry with
        :type tags: List[str]
        """
        tags = [Tag(tag) for tag in tags]
        entry = Entry(content, tags=tags)
        self._backend.write_entry(entry)

    def print_entries(self, display_max: int = 10, after: datetime = datetime.now() - timedelta(days=1), **kwargs):
        """
        Prints entries to terminal. By default, limits to
        the previous 10 results and shows up to 10.

        Default kwargs:
        :param display_max: max # of results to show
        :type display_max: int
        :param after: datetime to print entries after
        :see: `Controller._filter_kwargs` for more display options
        """
        kwargs['after'] = after
        filter_settings = self._parse_filter_kwargs(kwargs)
        entries = self._backend.read_entries(filter=filter_settings)
        terminal_frontend = TerminalFrontend(max_results=display_max)
        terminal_frontend.show(entries)

    def _parse_filter_kwargs(self, kwargs):
        filter_kwargs = {}
        for kwarg, value in kwargs.items():
            if kwarg not in self._filter_kwargs:
                raise TypeError('Invalid kwarg: {}'.format(kwarg))
            else:
                filter_kwargs[kwarg] = value
        return EntryFilterSettings(**filter_kwargs)

    def _init_backend(self):
        backend_type = get_config("backend")
        backend = None
        if backend_type is None:
            raise MissingConfigError("Backend type not specified in config")
        elif backend_type == "sqlite":
            path_to_db = get_config("backend_dir")
            if path_to_db is None:
                raise MissingConfigError("Backend location not specified in config")
            path(path_to_db).mkdir(exist_ok=True, parents=True)
            path_to_db = str(path(path_to_db, "todayi.db"))
            backend = SqliteBackend(path_to_db)
        else:
            raise InvalidConfigError(
                "Backend type: {} not supported".format(backend_type)
            )
        self._cached_backend = backend
