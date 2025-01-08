import structlog

from localllm.application.use_cases.interfaces import StoreAlbumUseCase
from localllm.domain.multimedia import Album
from localllm.domain.ports.persistence import AlbumRepository

logger = structlog.getLogger(__name__)


class StoreAlbums(StoreAlbumUseCase):
    """
    Use case to store albums in a repository.
    """  # noqa: D200

    def __init__(self, repository: AlbumRepository = None):
        self.repository = repository
        if self.repository:
            logger.info("Initializing repository")
            self.repository.initialize()

    def store_albums(self, albums: list[Album]) -> list[Album]:
        """
        Store albums to a repository.

        :param albums: list of Album to save.
        :return: list of Album stored.
        """
        if not self.repository:
            logger.info("No repository configured, skipping save")
            return []

        for album in albums:
            logger.info(f"Storing album to repository - {album.album_id} / {album.title} by {album.artist}")
            entity_id, album = self.repository.create_album(album)
            logger.info(f"Album with album_id {album.album_id} stored into repository with id {entity_id}")
        logger.info("All albums stored in repository")
        return albums
