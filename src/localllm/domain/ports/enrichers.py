from typing import Protocol


class AlbumEnricher(Protocol):
    """
    Generic interface for enrich album metadata.

    This interface defines the contract for enriching album metadata for an external
    source.
    """

    def get_album_metadata(self, artist: str, album: str) -> dict:
        """
        Retrieves album metadata from external source.

        :param artist: str, the artist of the album
        :param album: str, the title of the album
        :return: dict, the metadata of the album
        """
        pass
