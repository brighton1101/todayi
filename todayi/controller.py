from datetime import datetime, timedelta
from pathlib import Path
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
from todayi.remote.base import Remote
from todayi.remote.gcs import GcsRemote
from todayi.util.fs import path


class Controller:
    """
    Main application controller that coordinates resources.
    """

    _filter_kwargs = [
        "content_contains",
        "content_equals",
        "content_not_contains",
        "content_not_equals",
        "after",
        "before",
        "with_tags",
        "without_tags",
    ]

    def __init__(self):
        self._cached_backend = None
        self._cached_remote = None
        self._filter_kwargs = set(self._filter_kwargs)

    @property
    def _backend(self) -> Backend:
        if self._cached_backend is None:
            self._init_backend()
        return self._cached_backend

    @property
    def _remote(self) -> Remote:
        if self._cached_remote is None:
            self._init_remote()
        return self._cached_remote

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

    def print_entries(
        self,
        display_max: int = 10,
        after: datetime = datetime.now() - timedelta(days=1),
        **kwargs
    ):
        """
        Prints entries to terminal. By default, limits to
        the previous 10 results and shows up to 10.

        Default kwargs:
        :param display_max: max # of results to show
        :type display_max: int
        :param after: datetime to print entries after
        :see: `Controller._filter_kwargs` for more display options
        """
        kwargs["after"] = after
        filter_settings = self._parse_filter_kwargs(kwargs)
        entries = self._backend.read_entries(filter=filter_settings)
        terminal_frontend = TerminalFrontend(max_results=display_max)
        terminal_frontend.show(entries)

    def push_remote(self):
        """
        Pushes current backend to remote. Overwrites
        existing backend in remote.
        """
        self._remote.push()

    def pull_remote(self, backup_local: bool = False):
        """
        Pulls current backend from remote. Overwrites
        existing backend locally by default.

        :param backup_local: optionally backs up local backend file
        :type backup_local: bool
        """
        if backup_local == True:
            self._backend_file_path.rename(
                path(
                    self._backend_path,
                    "{}.{}".format(
                        self._backend_filename,
                        datetime.now().strftime("%m.%d.%Y-%H.%M.%S"),
                    ),
                )
            )
        self._remote.pull()

    def _parse_filter_kwargs(self, kwargs):
        filter_kwargs = {}
        for kwarg, value in kwargs.items():
            if kwarg not in self._filter_kwargs:
                raise TypeError("Invalid kwarg: {}".format(kwarg))
            else:
                filter_kwargs[kwarg] = value
        return EntryFilterSettings(**filter_kwargs)

    def _init_backend(self):
        backend_type = get_config("backend").lower()
        backend = None
        if backend_type is None:
            raise MissingConfigError("Backend type not specified in config")
        elif backend_type == "sqlite":
            backend = SqliteBackend(str(self._backend_file_path))
        else:
            raise InvalidConfigError(
                "Backend type: {} not supported".format(backend_type)
            )
        self._cached_backend = backend

    def _init_remote(self):
        remote_type = get_config("remote").lower()
        remote = None
        if remote_type is None:
            raise MissingConfigError("Remote type not specified in config")
        elif remote_type == "gcs":
            bucket_name = get_config("gcs_bucket_name")
            remote = GcsRemote(
                str(self._backend_file_path), self._backend_filename, bucket_name
            )
        else:
            raise InvalidConfigError(
                "Remote type: {} not supported".format(remote_type)
            )
        self._cached_remote = remote

    @property
    def _backend_filename(self) -> str:
        backend_filename = get_config("backend_filename")
        if backend_filename is None or backend_filename == "":
            raise MissingConfigError("Backend filename not specified in config")
        return backend_filename

    @property
    def _backend_path(self) -> Path:
        backend_dir = path(get_config("backend_dir"))
        if backend_dir is None or backend_dir == "":
            raise MissingConfigError("Backend location not specified in config")
        backend_dir.mkdir(exist_ok=True, parents=True)
        return backend_dir

    @property
    def _backend_file_path(self) -> Path:
        return path(self._backend_path, self._backend_filename)
