from abc import ABC, abstractmethod
from datetime import datetime


class Remote(ABC):
    @abstractmethod
    def push(self, backup: bool = False):
        """
        Pushes up current state to remote.
        """
        pass

    @abstractmethod
    def pull(self, backup: bool = False):
        """
        Updates current state from remote.
        """
        pass

    def _backup_file_name(self, orig_name: str) -> str:
        """
        Given the original file name, create a backup filename using
        the current time.

        :param orig_name: the original name of the file
        :type orig_name: str
        :return: str
        """
        return "{}.{}".format(orig_name, datetime.now().strftime("%m.%d.%Y-%H.%M.%S"))
