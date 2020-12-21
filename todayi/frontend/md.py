from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from jinja2 import Template

from todayi.frontend.base import FileFrontend
from todayi.model.entry import Entry
from todayi.util.fs import write_file
from todayi.util.iter import is_iterable


class MdSection(ABC):

    bullet_datetime_format = "%m-%d-%Y, %H:%M"

    def __init__(self, entries: List[Entry], group_key: Optional[Any] = None):
        self._entries = self.sort_section_entries(entries)
        self._group_key = group_key
        self._bullets = None

    @property
    def bullets(self):
        if self._bullets is None:
            self._bullets = [self.extract_bullet(e) for e in self._entries]
        return self._bullets

    def extract_bullet(self, e: Entry):
        return "{} - {}{}".format(
            e.created_at.strftime(self.bullet_datetime_format),
            e.content,
            ""
            if len(e.tags) < 1
            else " - Tags: {}".format(", ".join([t.name for t in e.tags])),
        )

    def sort_section_entries(self, entries: List[Entry]):
        return sorted(entries, key=lambda e: e.created_at)

    @property
    @abstractmethod
    def name(self):
        pass

    @staticmethod
    @abstractmethod
    def get_attr(e: Entry):
        pass

    @staticmethod
    def group_entries_by_section(cls, entries: List[Entry]):
        groups = defaultdict(list)
        for e in entries:
            keys = cls.get_attr(e)
            if not is_iterable(keys):
                keys = [keys]
            for key in keys:
                groups[key].append(e)
        return [cls(entries, group_key=key) for key, entries in groups.items()]


class DateSection(MdSection):

    bullet_datetime_format = "%H:%M"

    @property
    def name(self):
        return self._entries[0].created_at.strftime("%m-%d-%Y")

    @staticmethod
    def get_attr(e: Entry):
        return e.created_at.strftime("%m-%d-%Y")


class SingleTagSection(MdSection):
    @property
    def name(self):
        return self._group_key

    @staticmethod
    def get_attr(e: Entry):
        return [t.name for t in e.tags]


class MarkdownFrontend(FileFrontend):

    extension = "md"

    allowed_section_groupings = {
        "created_at": DateSection,
        "single_tag": SingleTagSection,
    }

    template = Template(
        """{% for section in sections %}
## {{section.name}}:{% for bullet in section.bullets %}
- {{bullet}}{% endfor %}
{% endfor %}
    """.strip(
            "\n"
        )
    )

    def __init__(self, output_file: str, section_grouping: str = "created_at"):
        if section_grouping not in self.allowed_section_groupings.keys():
            raise KeyError(
                "Invalid section grouping. Allowed: \n {}".format(
                    "\n".join(self.allowed_section_groupings.keys())
                )
            )
        self._group_by = section_grouping
        FileFrontend.__init__(self, output_file)

    def show(self, entries: List[Entry]):
        """
        Creates csv file from list of entries ordered
        by date.

        :param entries: entries to be displayed
        :type entries: List[Entry]
        """
        content = self.to_string(entries)
        write_file(content, self._output_file)

    def to_string(self, entries: List[Entry]) -> str:
        """
        Does the same thing as `Frontend.show`,
        but instead of writing to file returns
        file contents as string
        """
        sections = MdSection.group_entries_by_section(
            self.allowed_section_groupings.get(self._group_by), entries
        )
        return self.template.render(sections=sections).strip("\n")
