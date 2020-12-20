from collections import defaultdict
from typing import List, Optional

import requests

from todayi.frontend.base import Frontend, FileFrontend
from todayi.model.entry import Entry


class GistFrontend(Frontend):
    """
    For posting injected FileFrontend's contents to a Github Gist,
    rather than writing directly to file.

    :param auth: Github auth token
    :type auth: str
    :param gist_name: extensionless name of gist
    :type gist_name: str
    :param ff: file frontend to produce desired content type
    :type ff: FileFrontend
    :param public: Optionally make gist public (default not)
    :type public: bool
    """

    _gist_endpoint = "https://api.github.com/gists"

    def __init__(
        self, auth: str, gist_name: str, ff: FileFrontend, public: bool = False
    ):
        self._auth_token = auth
        self._gist_name = "{}.{}".format(gist_name, ff.extension)
        self._ff = ff
        self._public = public

    @property
    def github_headers(self):
        return {
            "Authorization": "token {}".format(self._auth_token),
            "Accept": "application/vnd.github.v3+json",
        }

    def show(self, entries: List[Entry]) -> str:
        """
        Posts gist to github using content given by injected FileFrontend's
        `to_string` method.

        :param entries: entries to post gist for
        :type entries: List[Entry]
        :return: str with html url to new gist
        """
        req_body = defaultdict(dict)
        req_body["files"][self._gist_name] = {
            "content": self._ff.to_string(entries),
        }
        req_body["public"] = self._public
        res = requests.post(
            self._gist_endpoint, json=req_body, headers=self.github_headers
        )
        if res.status_code == 401:
            raise GistError(
                "Unauthorized response from Github. "
                "Ensure access token has appropriate perms "
                "for gists."
            )
        elif res.status_code != 201:
            raise GistError("Unknown error ocurred creating Gist.")
        return res.json().get("html_url")


class GistError(Exception):
    pass
