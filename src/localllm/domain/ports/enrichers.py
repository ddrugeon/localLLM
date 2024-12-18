from typing import Protocol

from localllm.domain.multimedia import Album


class AlbumEnricher(Protocol):
    """
    Generic interface for enrich album metadata.

    This interface defines the contract for enriching album metadata for an external
    source.
    """

    async def get_album_metadata(self, artist: str, album: str) -> Album | None:
        """
        Retrieves album metadata from external source.

        :param artist: str, the artist of the album
        :param album: str, the title of the album
        :return: Album, the metadata of the album or None if not found
        """
        pass
