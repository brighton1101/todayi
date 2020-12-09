from abc import ABC, abstractmethod


class Remote(ABC):

    @abstractmethod
    def push(self):
        """
        Pushes up current state to remote.
        """
        pass

    @abstractmethod
    def pull(self):
        """
        Updates current state from remote.
        """
        pass
