from pathlib import Path
from typing import Protocol

from localllm.domain.multimedia import Album


class LoadAlbumUseCase(Protocol):
    def load_albums(self, file_path: Path) -> list[Album]:
        """
        Load albums from a file.

        :param file_path: the path to the file to load.
        :return: list of Album loaded from the file.
        """
        raise NotImplementedError


class StoreAlbumUseCase(Protocol):
    def store_albums(self, albums: list[Album]) -> list[Album]:
        """
        Store albums to a repository.

        :param albums: list of Album to save.
        :return: list of Album stored.
        """
        raise NotImplementedError


class EnrichAlbumUseCase(Protocol):
    async def enrich_albums(self, albums: list[Album]):
        """
        Enrich albums with additional information from an external source.

        :param albums: list of Album to enrich.
        """
        raise NotImplementedError


class IndexAlbumUseCase(Protocol):
    def index_albums(self, albums: list[Album]):
        """
        Index albums in a vector database.

        :param albums: list of Album to index.
        """
        raise NotImplementedError

    def search_albums(self, query: str, top_k: int = 5) -> list[Album]:
        """
        Search for albums in a vector database.

        :param query: the query to search for.
        :param top_k: the number of results to return.
        """
        raise NotImplementedError
