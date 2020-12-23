from pathlib import Path

from todayi.util.fs import path


def test_path_str():
    assert (
        str(path("~/Desktop", "hello", "world")) == f"{Path.home()}/Desktop/hello/world"
    )


def test_path_pathlib():
    assert str(path(Path.home(), "hello")) == f"{Path.home()}/hello"
