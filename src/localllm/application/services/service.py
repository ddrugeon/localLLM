from pathlib import Path

import structlog
from localllm import DiscogsAlbumEnricher
from localllm.domain.multimedia import Album

from localllm.domain.ports.fetchers import AlbumFileReader

logger = structlog.getLogger()


class MultimediaService:
    """Service class for our multimedia assistant."""

    def __init__(self, fetcher: AlbumFileReader, discogs_enricher: DiscogsAlbumEnricher = None):
        self.album_file_reader = fetcher
        self.discogs_enricher = discogs_enricher

    def load_albums(self, album_file_path: Path) -> list[Album]:
        """Loads albums from file."""
        logger.info(f"Loading albums from {album_file_path}")
        albums = self.album_file_reader.read(path=album_file_path)
        logger.info(f"{len(albums)} albums loaded")
        return albums

    def enrich_albums(self, albums: list[Album]) -> list[dict]:
        """Enriches albums metadata."""
        logger.info("Enriching albums")
        enriched_albums = []

        album = albums[0]
        if self.discogs_enricher:
            enriched_albums.append(self.discogs_enricher.get_album_metadata(artist=album.artist, album=album.title))

        return enriched_albums