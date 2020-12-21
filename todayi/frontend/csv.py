import csv
from io import StringIO
from typing import List

from todayi.frontend.base import (
    FileFrontend,
    FrontendAttribute,
    entry_content,
    entry_when,
    entry_tags_csv_str,
)
from todayi.model.entry import Entry
from todayi.util.fs import write_file


class CsvFrontend(FileFrontend):

    extension = "csv"

    _default_attributes = [
        FrontendAttribute("content", entry_content),
        FrontendAttribute("when", entry_when),
        FrontendAttribute("tags", entry_tags_csv_str),
    ]

    def show(self, entries: List[Entry]):
        """
        Creates markdown from list of entries ordered
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
        rows = [self._get_headers()]
        rows.extend(self._get_rows(entries))
        output = StringIO()
        csvwriter = csv.writer(output, delimiter=",")
        csvwriter.writerows(rows)
        output.seek(0)
        return output.read()
