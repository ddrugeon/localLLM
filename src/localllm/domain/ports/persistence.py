from typing import Protocol

from localllm.domain.multimedia import Album


class AlbumRepository(Protocol):
    def initialize(self) -> None:
        """
        Initializes the document storage system.

        :return: None
        """
        pass

    def create_album(self, album: Album) -> (str, Album):
        """
        Saves an album to the storage.

        :param album: Album, the album to be saved
        :return: Album, the saved document with any additional metadata
        """
        pass

    def get_number_albums(self) -> int:
        """
        Retrieves total number of albums from the storage.

        :return: int, number of albums present in storage
        """
        pass

    def get_albums(self) -> list[Album]:
        """
        Retrieves all albums from the storage.

        :return: list[Album], the list of all albums
        """
        pass

    def get_album_by_id(self, album_id: str) -> Album:
        """
        Retrieves an album by its ID.

        :param album_id: str, the ID of the album
        :return: Album, the album with the given ID
        :raise AlbumNotFoundError: if the album is not found
        """
        pass

    def search_albums(self, query: str, top_k: int = 3) -> list[Album]:
        """
        Searches for relevant albums based on a query.

        :param query: str, the search query on title or artist name (or both).
            Example: "artist:artist_name title:album_title"
        :param top_k: int, maximum number of albums to return
        :return: List[Document], the most relevant albums
        """
        pass

    def search_albums_by_metadata(self, metadata: dict, top_k: int = 3) -> list[Album]:
        """
        Searches for albums matching specific metadata criteria.

        :param metadata: dict, metadata key-value pairs to match
        :param top_k: int, maximum number of albums to return
        :return: List[Document], the matching albums
        """
        pass

    def update_album(self, album_id: int, updated_album: Album) -> Album | None:
        """
        Updates an existing album in the storage.

        :param album_id: int, the ID of the album to be updated
        :param updated_album: Album, the updated album data
        :return: Album, the updated album or None if not found
        """
        pass
