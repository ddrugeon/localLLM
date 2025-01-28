from pathlib import Path

import structlog

from localllm.application.use_cases.interfaces import (
    EnrichAlbumUseCase,
    FileStorageAlbumUseCase,
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
        file_storage_album_use_case: FileStorageAlbumUseCase = None,
    ):
        self._load_albums_use_case = load_albums_use_case
        self._enrich_album_use_case = enrich_album_use_case
        self._store_albums_use_case = store_albums_use_case
        self._index_albums_use_case = index_albums_use_case
        self._file_storage_album_use_case = file_storage_album_use_case

    def load_albums(self, album_file_path: Path) -> list[Album]:
        """
        Load albums from a file.

        :param album_file_path: Path to the file containing the albums.
        :return: list of Album loaded.
        """
        logger.info(f"Loading albums from {album_file_path}")
        return self._load_albums_use_case.load_albums(file_path=album_file_path)

    async def enrich_albums(self, albums: list[Album]) -> list[Album]:
        """
        Enrich albums with metadata from external sources.

        :param albums: Albums to enrich.
        :return: Enriched albums.
        """
        logger.info("Enriching albums")
        return await self._enrich_album_use_case.enrich_albums(albums)

    async def store_albums(self, albums: list[Album]) -> list[Album]:
        """
        Store albums to a repository.

        :param albums: Albums to save.
        :return: Albums saved.
        """
        logger.info("Storing albums to repository")
        return self._store_albums_use_case.store_albums(albums)

    def save_albums(self, albums: list[Album], path: Path) -> None:
        """
        Save albums to a file.

        :param albums: Albums to save.
        :param path: Path to the file to save.
        :return: None.
        """
        logger.info(f"Saving albums to {path}")
        self._file_storage_album_use_case.persist(albums, path)

    def index_albums(self, albums: list[Album]) -> list[Album]:
        logger.info("Indexing albums")
        return self._index_albums_use_case.index_albums(albums)

    def search_albums(self, query: str, top_k: int = 5) -> list[tuple[Album, float]]:
        logger.info(f"Search album from query: {query}")
        return self._index_albums_use_case.search_albums(query, top_k=top_k)
