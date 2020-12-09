from typing import List

from todayi.backend.base import Backend
from todayi.backend.sqlite import SqliteBackend
from todayi.config import (
    get as get_config,
    set as set_config,
    MissingConfigError,
    InvalidConfigError,
)
from todayi.model.entry import Entry
from todayi.model.tag import Tag
from todayi.util.fs import path


class Controller:
    def __init__(self):
        self._cached_backend = None

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
