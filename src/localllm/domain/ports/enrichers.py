from typing import Protocol


class AlbumEnricher(Protocol):
    """Generic interface for enrich album metadata."""

    def get_album_metadata(self, artist: str, album: str) -> dict:
        """Retrieves album metadata from external source."""
        pass
