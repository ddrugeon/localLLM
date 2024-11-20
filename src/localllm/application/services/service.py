from pathlib import Path

import structlog

from localllm.domain.multimedia import Album
from localllm.domain.ports.enrichers import AlbumEnricher
from localllm.domain.ports.fetchers import AlbumFileReader

logger = structlog.getLogger()


class MultimediaService:
    """
    Service class for our multimedia assistant.

    It loads albums from a file and enriches them with metadata issued from an external
    source.
    """

    def __init__(self, fetcher: AlbumFileReader, enricher: AlbumEnricher = None):
        self.album_file_reader = fetcher
        self.discogs_enricher = enricher

    def load_albums(self, album_file_path: Path) -> list[Album]:
        """
        Loads albums from file.

        It fetches albums from a file and returns them as a list of Album objects.
        :param album_file_path: Path to the file containing albums.
        :return: List of Album objects.
        """

        logger.info(f"Loading albums from {album_file_path}")
        albums = self.album_file_reader.read(path=album_file_path)
        logger.info(f"{len(albums)} albums loaded")
        return albums

    def enrich_albums(self, albums: list[Album]) -> list[dict]:
        """
        Enriches albums metadata.

        It enriches albums metadata using an external source.
        :param albums: List of Album objects.
        :return: List of enriched albums metadata.gaa
        """
        logger.info("Enriching albums")
        enriched_albums = []

        album = albums[0]
        if self.discogs_enricher:
            enriched_albums.append(
                self.discogs_enricher.get_album_metadata(
                    artist=album.artist, album=album.title
                )
            )

        return enriched_albums
