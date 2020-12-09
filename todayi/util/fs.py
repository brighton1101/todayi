"""
Module used to interact with filesystem.
"""

from pathlib import Path
from typing import Union, Tuple


def path(*fp: Tuple[str]) -> Path:
    """
    Gets path given within users' home
    directory.

    :param fp: file path to expand to users' home directory
    :type fp: positional args
    :return: Path
    """
    return Path(*fp).expanduser()


def _resolve_fp(fp: Union[str, Path]) -> Path:
    if isinstance(fp, str):
        fp = path(fp)
    return fp


def file_text(fp: Union[str, Path]) -> str:
    """
    Reads text from file.

    :param fp: file path in string format to
    """
    return _resolve_fp(fp).read_text()


def write_file(content: str, fp: Union[str, Path]):
    return _resolve_fp(fp).write_text(content)
