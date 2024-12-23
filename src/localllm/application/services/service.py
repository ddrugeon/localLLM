import asyncio
from pathlib import Path

import structlog

from localllm.domain.multimedia import Album
from localllm.domain.ports.enrichers import AlbumEnricher
from localllm.domain.ports.fetchers import AlbumFileReader
from localllm.domain.ports.persistence import AlbumRepository

logger = structlog.getLogger()


class MultimediaService:
    """
    Service class for our multimedia assistant.

    It loads albums from a file and enriches them with metadata issued from an external
    source.
    """

    def __init__(
        self,
        fetcher: AlbumFileReader | None = None,
        enrichers: list[AlbumEnricher] = None,
        repository: AlbumRepository = None,
    ):
        self.album_file_reader = fetcher
        self.enrichers = enrichers or []
        self.repository = repository

        if self.repository:
            self.repository.initialize()

    def load_albums(self, album_file_path: Path) -> list[Album]:
        logger.info(f"Loading albums from {album_file_path}")
        if self.album_file_reader:
            albums = self.album_file_reader.read(path=album_file_path)
            logger.info(f"{len(albums)} albums loaded")
            return albums
        logger.info("No fetcher configured, returning empty list")
        return []

    async def save_albums(self, albums: list[Album], enrich_album: bool = False) -> list[Album]:
        async def process_album(album: Album) -> Album:
            try:
                if enrich_album:
                    album = await self._enrich_album(album)
            except Exception as e:
                logger.error(f"Error when enriching album {album.title}: {e}")
            try:
                album = await self._save_album(album)
            except Exception as e:
                logger.error(f"Error saving album {album.title}: {e}")
            return album

        tasks = [process_album(album) for album in albums]
        saved_albums = await asyncio.gather(*tasks, return_exceptions=True)
        return [current for current in saved_albums if isinstance(current, Album)]

    async def _enrich_album(self, album: Album) -> Album:
        logger.info("Enriching album")
        tasks = [enricher.get_album_metadata(album.artist, album.title) for enricher in self.enrichers]
        results = await asyncio.gather(*tasks)

        combined_metadata = album.model_dump()
        for metadata in results:
            if metadata:
                combined_metadata.update({k: v for k, v in metadata.dict().items() if v is not None})

        return Album(**combined_metadata)

    async def _save_album(self, album: Album) -> Album:
        logger.info(f"Saving album to repository - {album.album_id}")
        if self.repository:
            album = self.repository.create_album(album)
            logger.info(f"Album with album_id {album.album_id} saved")
        else:
            logger.info("No repository configured, skipping save")

        return album
