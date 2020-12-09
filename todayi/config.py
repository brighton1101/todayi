"""
Module used to interact with configuration file.
By default, if configuration file does not exist
the default config is written to a file at
the specified CONFIG_PATH within users' home
directory.
"""

import json
from typing import Any

from todayi.util.fs import path, file_text, write_file


CONFIG_PATH = "~/todayi.config"


DEFAULT_CONFIG = {
    "backend": "sqlite",
    "backend_dir": "~/todayi/",
    "remote": "GCS",
    "remote_address": None,
}


file_path = path(CONFIG_PATH)


def _check_key(key):
    if key not in DEFAULT_CONFIG.keys():
        raise IndexError("Config: {} is not valid".format(key))


def _read_config():
    return json.loads(file_text(file_path))


def _write_config(config):
    return write_file(json.dumps(config), file_path)


"""
If config not present, write the default
"""
if not file_path.is_file():
    _write_config(DEFAULT_CONFIG)


def get(key: str) -> Any:
    """
    Gets value of config from key

    :param key: config key
    :type key: str
    :return: config value
    """
    _check_key(key)
    config = _read_config()
    return config.get(key, DEFAULT_CONFIG.get(key))


def set(key: str, value: Any):
    """
    Sets key/value pair in config

    :param key: config key
    :type key: str
    :param value: value to be set
    :type value: Any
    """
    _check_key(key)
    config = _read_config()
    config[key] = value
    _write_config(config)


class MissingConfigError(Exception):
    """
    Error to use when config values are missing
    """

    pass


class InvalidConfigError(Exception):
    """
    Error to use when config values are missing
    """

    pass
