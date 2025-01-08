from pathlib import Path

import structlog

from localllm.application.use_cases.interfaces import (
    EnrichAlbumUseCase,
    IndexAlbumUseCase,
    LoadAlbumUseCase,
    StoreAlbumUseCase,
)
from localllm.domain.multimedia import Album

logger = structlog.getLogger()


class MultimediaIngesterService:
    """
    Service class for our multimedia assistant.

    It loads albums from a file and enriches them with metadata issued from an external
    source.
    """

    def __init__(
        self,
        load_albums_use_case: LoadAlbumUseCase,
        enrich_album_use_case: EnrichAlbumUseCase,
        store_albums_use_case: StoreAlbumUseCase,
        index_albums_use_case: IndexAlbumUseCase,
    ):
        self._load_albums_use_case = load_albums_use_case
        self._enrich_album_use_case = enrich_album_use_case
        self._store_albums_use_case = store_albums_use_case
        self._index_albums_use_case = index_albums_use_case

    def load_albums(self, album_file_path: Path) -> list[Album]:
        """
        Load albums from a file.

        :param album_file_path: Path to the file containing the albums.
        :return: list of Album loaded.
        """
        logger.info(f"Loading albums from {album_file_path}")
        return self._load_albums_use_case.load_albums(file_path=album_file_path)

    async def save_albums(self, albums: list[Album], enrich_album: bool = False) -> list[Album]:
        """
        Save albums to a repository.

        If enrich_album is True, enrich the album metadata from external sources before
        saving.

        :param albums: Albums to save.
        :param enrich_album: True if the albums should be enriched before saving.
        :return: Albums saved.
        """
        logger.info("Storing albums to repository")
        if enrich_album:
            logger.info("Eriching albums")
            albums = await self._enrich_album_use_case.enrich_albums(albums)
        return self._store_albums_use_case.store_albums(albums)

    def index_albums(self, albums: list[Album]) -> list[Album]:
        logger.info("Indexing albums")
        return self._index_albums_use_case.index_albums(albums)

    def search_albums(self, query: str) -> list[Album]:
        logger.info(f"Search album from query: {query}")
        return self._index_albums_use_case.search_albums(query)
