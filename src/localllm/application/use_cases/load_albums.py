from pathlib import Path

import structlog

from localllm.application.use_cases.interfaces import LoadAlbumUseCase
from localllm.domain.multimedia import Album
from localllm.domain.ports.fetchers import AlbumFileReader

logger = structlog.getLogger(__name__)


class LoadAlbums(LoadAlbumUseCase):
    def __init__(self, fetcher: AlbumFileReader | None = None):
        self.fetcher = fetcher

    def load_albums(self, file_path: Path) -> list[Album]:
        """
        Load albums from a file.

        :param file_path: Path to the file to load.
        :return: List of Album loaded from the file.
        """
        logger.info(f"Loading albums from {file_path}")

        if not self.fetcher:
            logger.info("No fetcher configured, returning empty list")
            return []

        albums = self.fetcher.read(path=file_path)
        logger.info(f"{len(albums)} albums loaded")
        return albums
