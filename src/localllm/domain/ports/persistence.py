from typing import Protocol

from localllm.domain.multimedia import Album


class AlbumPersistence(Protocol):
    def initialize(self):
        """
        Initializes the database by creating all tables.

        :return: None
        """
        pass

    def create_album(self, album: Album) -> Album:
        """
        Saves an album to the database.

        :param album: Album, the album to be saved
        :return: None
        """
        pass

    def get_number_albums(self) -> int:
        """
        Retrieves number of albums from the database.

        :return: int, number of albums present in database
        """
        pass

    def get_albums(self) -> list[Album]:
        """
        Retrieves all albums from the database.

        :return: list[Album], the list of all albums
        """
        pass

    def get_album_by_id(self, album_id: str) -> Album:
        """
        Retrieves an album by its ID from the database.

        :param album_id: str, the ID of the album
        :return: Album, the album with the specified ID
        :raises: AlbumNotFoundError, if the album is not found
        """
        pass

    def get_albums_by_title(self, title: str) -> list[Album]:
        """
        Retrieves albums by their title from the database.

        :param title: str, the title of the albums
        :return: list[Album], the list of albums with the specified title
        """
        pass

    def get_albums_by_artist(self, artist: str) -> list[Album]:
        """
        Retrieves albums by their artist from the database.

        :param artist: str, the artist of the albums
        :return: list[Album], the list of albums with the specified artist
        """
        pass

    def get_albums_by_genres(self, genres: list[str]) -> list[Album]:
        """
        Retrieves albums by their genres from the database.

        :param artist: list[str], the genres of the albums
        :return: list[Album], the list of albums with the specified artist
        """
        pass

    def update_album(self, album_id: int, updated_album: Album) -> Album | None:
        """
        Updates an existing album in the database.

        :param album_id: int, the ID of the album to be updated
        :param updated_album: Album, the updated album data
        :return: Album, the updated album or None if not found
        """
        pass
