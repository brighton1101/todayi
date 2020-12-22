from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Union

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
from todayi.frontend.csv import CsvFrontend
from todayi.frontend.gist import GistFrontend
from todayi.frontend.md import MarkdownFrontend
from todayi.model.entry import Entry
from todayi.model.tag import Tag
from todayi.remote.base import Remote
from todayi.remote.gcs import GcsRemote
from todayi.remote.git import GitRemote
from todayi.util.fs import path


class Controller:
    """
    Main application controller that coordinates resources.
    """

    """
    Helper functions to parse filtering command line
    args.
    """

    def parse_comma_sep(s: Union[str, List[str]]) -> List[str]:
        if isinstance(s, list):
            return s
        o = s.split(",")
        return [e.strip() for e in o]

    def parse_datetime(d: Union[str, datetime]) -> datetime:
        if isinstance(d, datetime):
            return d
        return datetime.strptime(d.strip(), "%m/%d/%Y")

    def parse_str(s: str) -> str:
        return s.strip()

    def parse_tags(s: Union[str, List[str]]) -> List[Tag]:
        if isinstance(s, str):
            s = Controller.parse_comma_sep(s)
        return [Tag(t) for t in s]

    """
    Available filter kwargs, as to be passed in via
    cli.
    """
    filter_kwargs = {
        "content_contains": parse_str,
        "content_equals": parse_str,
        "content_not_contains": parse_str,
        "content_not_equals": parse_str,
        "after": parse_datetime,
        "before": parse_datetime,
        "with_tags": parse_tags,
        "without_tags": parse_tags,
    }

    _file_frontends = {
        "csv": CsvFrontend,
        "md": MarkdownFrontend,
    }

    def __init__(self):
        self._cached_backend = None
        self._cached_remote = None
        self._filter_kwargs = self.filter_kwargs

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

    def print_entries(self, display_max: int = 10, **kwargs):
        """
        Prints entries to terminal. By default, limits to
        the previous 10 results and shows only results for
        the last day.

        Default kwargs:
        :param display_max: max # of results to show
        :type display_max: int
        :see: `Controller.filter_kwargs` for more display options
        """
        after = kwargs["after"]
        kwargs["after"] = datetime.now() - timedelta(days=1) if after is None else after
        filter_settings = self._parse_filter_kwargs(kwargs)
        entries = self._backend.read_entries(filter=filter_settings)
        terminal_frontend = TerminalFrontend(max_results=display_max)
        terminal_frontend.show(entries)

    def push_remote(self, backup_remote: bool = False):
        """
        Pushes current backend to remote. Overwrites
        existing backend in remote.
        """
        self._remote.push(backup=backup_remote)

    def pull_remote(self, backup_local: bool = False):
        """
        Pulls current backend from remote. Overwrites
        existing backend locally by default.

        :param backup_local: optionally backs up local backend file
        :type backup_local: bool
        """
        self._remote.pull(backup=backup_local)

    def file_report(self, format: str, output_file: str, **kwargs):
        """
        Generates a file report of entries.

        :param format: file format to use. see `Controller._file_frontends`
                       for configuration
        :type format: str
        :param output_file: absolute path to file location to output report
        :type output_file: str
        :see: `Controller.filter_kwargs` for more display options
        """
        filter_settings = self._parse_filter_kwargs(kwargs)
        entries = self._backend.read_entries(filter=filter_settings)
        frontend = self._init_file_frontend(format, output_file)
        frontend.show(entries)

    def gist_report(
        self, format: str, output_name: str, public: bool = False, **kwargs
    ):
        """
        Generates a Github gist report with given file format of entries.

        :param format: file format to use. see `Controller._file_frontends`
                       for configuration
        :type format: str
        :param output_name: name of gist (not including extension)
        :type output_name: str
        :param public: whether or not to make gist public (by default False)
        :type public: bool
        :see: `Controller.filter_kwargs` for more display options
        """
        filter_settings = self._parse_filter_kwargs(kwargs)
        entries = self._backend.read_entries(filter=filter_settings)
        if len(entries) < 1:
            raise NoMatchingEntriesError(
                "No matching entries. Github does not allow for empty gists."
            )
        auth_token = get_config("github_auth_token")
        if auth_token is None or auth_token == "":
            raise MissingConfigError(
                "Could not find auth token for ghub. Please provide the config key "
                "`github_auth_token` with a valid auth token and try again"
            )
        ff = self._init_file_frontend(format, output_name)
        gf = GistFrontend(auth_token, output_name, ff, public=public)
        gf.show(entries)

    def read_config(self, key: str) -> str:
        return get_config(key)

    def write_config(self, key: str, val: str):
        set_config(key, val.strip())

    def _init_file_frontend(self, form: str, o_file: str):
        ff = self._file_frontends.get(form)
        if ff is None:
            raise TypeError("Invalid file frontend format: {}".format(form))
        return ff(o_file)

    def _parse_filter_kwargs(self, kwargs):
        filter_kwargs = {}
        for kwarg, value in kwargs.items():
            if kwarg not in self._filter_kwargs:
                raise TypeError("Invalid kwarg: {}".format(kwarg))
            elif value is not None:
                filter_kwargs[kwarg] = self._filter_kwargs.get(kwarg)(value)
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
        elif remote_type == "git":
            remote_uri = get_config("git_remote_uri")
            remote = GitRemote(str(self._backend_path), remote_uri)
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


class NoMatchingEntriesError(Exception):
    pass
