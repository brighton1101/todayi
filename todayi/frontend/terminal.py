from typing import List

from prettytable import PrettyTable

from todayi.frontend.base import Frontend, FrontendAttribute as Attr, entry_tags_csv_str, entry_when, entry_content
from todayi.model.entry import Entry


class TerminalFrontend(Frontend):
    """
    Frontend for viewing entries via the terminal.
    """

    def __init__(self, max_results=10):
        self._max_results = max_results

    def show(self, entries: List[Entry]):
        """
        Outputs entries to terminal in table
        format

        :param entries: entries to be displayed
        :type entries: List[Entry]
        """
        entries = sorted(entries, key=lambda e: e.created_at, reverse=True)
        entries = entries[0:min(len(entries), self._max_results)]
        if len(entries) == 0:
            print("No matching entries...")
            return
        table_headers = self._get_headers()
        parsed_rows = self._get_rows(entries)
        table = PrettyTable()
        table.field_names = table_headers
        table.add_rows(parsed_rows)
        print(table.get_string())
