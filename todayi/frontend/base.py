from abc import ABC, abstractmethod
from typing import Any, Callable, List, Union

from todayi.model.entry import Entry


def entry_content(e: Entry):
    return e.content


def entry_tags_csv_str(e: Entry) -> str:
    return ", ".join([t.name for t in e.tags])


def entry_when(e: Entry, time: bool = False) -> str:
    if time is True:
        return e.created_at.strftime("%Y-%m-%d %H:%M")
    return e.created_at.strftime("%Y-%m-%d")


class FrontendAttribute:
    def __init__(self, header: str, field: Union[str, Callable[[Entry], str]]):
        self.header = header
        self._field = field

    def field(self, e: Entry) -> Any:
        if isinstance(self._field, str):
            return e.__getattribute__(self._field)
        return self._field(e)


class Frontend(ABC):
    """
    Base class for viewing/exporting data.
    """

    _default_attributes = [
        FrontendAttribute("What was done:", entry_content),
        FrontendAttribute("When:", entry_when),
        FrontendAttribute("Tags:", entry_tags_csv_str),
    ]

    @abstractmethod
    def show(self, entries: List[Entry]):
        """
        'Shows' the data, whether that means
        outputting it via terminal, creating
        a MD file, etc.

        :param entries: entries to be displayed
        :type entries: List[Entry]
        """
        pass

    def _get_headers(self) -> List[str]:
        """
        Fetches data headers from default attributes

        :return: List[str]
        """
        return [a.header for a in self._default_attributes]

    def _get_rows(self, entries: List[Entry]) -> List[List[str]]:
        """
        Transforms List[Entry] into a List[List[str]]

        Example:
        ```
        >>> entries = [Entry(content='Hello world',
            created_at=datetime.now(), tags=['hello'])]
        >>> self._default_attributes = [FrontendAttribute('Content',
            lambda e: e.content)]
        >>> self._parse_rows(entries)
        [['Hello world']]

        :param entries: list of entries
        :type entries: List[Entry]
        :return: List[List[str]]
        """
        return [[a.field(e) for a in self._default_attributes] for e in entries]


class FileFrontend(Frontend, ABC):

    extension = ""

    def __init__(self, output_file: str):
        self._output_file = output_file

    @abstractmethod
    def to_string(self, entries: List[Entry]) -> str:
        """
        Does the same thing as `Frontend.show`,
        but instead of writing to file returns
        file contents as string
        """
        pass
