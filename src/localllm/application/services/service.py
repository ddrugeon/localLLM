from pathlib import Path

import structlog

from localllm.domain.ports.fetchers import AlbumFileReader
logger = structlog.getLogger()

class MultimediaService:
    """Service class for our multimedia assistant."""

    def __init__(self, fetcher: AlbumFileReader):
        self.album_file_reader = fetcher

    def load_albums(self, album_file_path: Path):
        """Loads albums from file."""
        logger.info(f'Loading albums from {album_file_path}')
        albums = self.album_file_reader.read(path=album_file_path)
        logger.info(f"{len(albums)} albums loaded")
        return albums