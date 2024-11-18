from typing import Protocol

from localllm.domain.multimedia import Album


class AlbumFileReader(Protocol):
    """Generic interface for reading albums from file."""

    def read(self, path: str) -> list[Album]:
        """Reads albums from file."""
        pass