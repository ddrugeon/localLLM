from pathlib import Path
from typing import Protocol

from localllm.domain.multimedia import Album


class AlbumFileReader(Protocol):
    """
    Generic interface for reading albums from file.

    This interface defines the contract for reading albums from file.
    """

    def read(self, path: Path) -> list[Album]:
        """
        Reads albums from file.

        :param path: Path, the path to the file
        :return: list[Album], the albums read from file
        """
        pass
