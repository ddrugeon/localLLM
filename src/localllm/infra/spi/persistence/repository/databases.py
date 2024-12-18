import structlog
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine

from localllm.domain.multimedia import Album, Track
from localllm.domain.ports.persistence import AlbumPersistence
from localllm.infra.spi.persistence.repository.models import AlbumEntity, TrackEntity

logger = structlog.getLogger()


class AlbumNotFoundError(Exception):
    """
    Exception raised when an album was not found in database.
    """ # noqa: D200

    pass


class AlbumSaveError(Exception):
    """
    Exception raised when an error occurs while saving an album.
    """ # noqa: D200

    pass


class AlbumUpdateError(Exception):
    """
    Exception raised when an error occurs while updating an album.
    """ # noqa: D200

    pass


# Adapter to transform Album from domain model to entities model
def _domain_to_entity(domain_album: Album) -> AlbumEntity:
    return AlbumEntity(
        id=None,  # Assuming the ID is auto-generated
        album_id=domain_album.album_id,
        title=domain_album.title,
        artist=domain_album.artist,
        year=domain_album.year,
        genres=domain_album.genres,
        styles=domain_album.styles,
        labels=domain_album.labels,
        country=domain_album.country,
        tracklist=[_domain_to_entity_track(track) for track in domain_album.tracklist],
        credits=domain_album.credits,
        external_urls=domain_album.external_urls,
        external_ids=domain_album.external_ids,
    )


# Adapter to transform Track from domain model to entities model
def _domain_to_entity_track(domain_track: Track) -> TrackEntity:
    return TrackEntity(
        id=None,  # Assuming the ID is auto-generated
        position=domain_track.position,
        title=domain_track.title,
        duration=domain_track.duration,
        album_id=None,  # This will be set when the album is saved
    )


# Adapter to transform Album from entities model to domain model
def _entity_to_domain(entity_album: AlbumEntity) -> Album:
    return Album(
        album_id=entity_album.album_id,
        title=entity_album.title,
        artist=entity_album.artist,
        year=entity_album.year,
        genres=entity_album.genres_list,
        styles=entity_album.styles_list,
        labels=entity_album.labels_list,
        country=entity_album.country,
        tracklist=[_entity_to_domain_track(track) for track in entity_album.tracklist],
        credits=entity_album.credits,
        external_urls=entity_album.external_urls_dict,
        external_ids=entity_album.external_ids_dict,
    )


# Adapter to transform Track from entities model to domain model
def _entity_to_domain_track(entity_track: TrackEntity) -> Track:
    return Track(
        position=entity_track.position,
        title=entity_track.title,
        duration=entity_track.duration,
    )


class DatabaseAlbumPersistence(AlbumPersistence):
    def __init__(self, db_url: str):
        logger.info(f"Connecting to database: {db_url}")
        self._engine = create_engine(db_url, echo=False)

    def initialize(self) -> None:
        """
        Initializes the database by creating all tables.

        :return: None
        """
        logger.info("Initializing the database")
        SQLModel.metadata.drop_all(self._engine, checkfirst=True)
        SQLModel.metadata.create_all(self._engine, checkfirst=True)

    def create_album(self, album: Album) -> Album:
        """
        Saves an album to the database.

        :param album: Album, the album to be saved
        :return: None
        """
        logger.info(f"Saving album: {album.title} by {album.artist}")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            try:
                entity = _domain_to_entity(domain_album=album)
                session.add(entity)
                session.commit()
                return _entity_to_domain(entity)
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving album: {e}")
                raise AlbumSaveError("Failed to save album") from e

    def get_number_albums(self) -> int:
        """
        Retrieves number of albums from the database.

        :return: int, number of albums present in database
        """
        logger.info("Getting number of albums")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            results = session.query(AlbumEntity)
            return len(results.all())

    def get_albums(self) -> list[Album]:
        """
        Retrieves all albums from the database.

        :return: list[Album], the list of all albums
        """
        logger.info("Retrieving all albums")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            results = session.query(AlbumEntity)
            return [_entity_to_domain(entity_album=entity) for entity in results.all()]

    def get_album_by_id(self, album_id: str) -> Album:
        """
        Retrieves an album by its ID from the database.

        :param album_id: int, the ID of the album
        :return: Album, the album with the specified ID or None if not found
        """
        logger.info(f"Retrieving album with ID: {album_id}")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            result = (
                session.query(AlbumEntity)
                .filter(AlbumEntity.album_id == album_id)
                .first()
            )
            if result:
                return _entity_to_domain(result)

            logger.error("Album not found")
            raise AlbumNotFoundError(f"Album with ID {album_id} not found")

    def get_albums_by_title(self, title: str) -> list[Album]:
        """
        Retrieves albums by their title from the database.

        :param title: str, the title of the albums
        :return: list[Album], the list of albums with the specified title
        """
        logger.info(f"Retrieving albums with title: {title}")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            results = session.query(AlbumEntity).filter(AlbumEntity.title == title)
            return [_entity_to_domain(entity_album=entity) for entity in results.all()]

    def get_albums_by_artist(self, artist: str) -> list[Album]:
        """
        Retrieves albums by their artist from the database.

        :param artist: str, the artist of the albums
        :return: list[Album], the list of albums with the specified artist
        """
        logger.info(f"Retrieving albums by artist: {artist}")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            results = session.query(AlbumEntity).filter(
                AlbumEntity.artist.contains(artist)
            )
            return [_entity_to_domain(entity_album=entity) for entity in results.all()]

    def update_album(self, album_id: int, updated_album: Album) -> Album | None:
        """
        Updates an existing album in the database.

        :param album_id: int, the ID of the album to be updated
        :param updated_album: Album, the updated album data
        :return: Album, the updated album or None if not found
        """
        logger.info(f"Updating album with ID: {album_id}")
        session_class = sessionmaker(self._engine)
        with session_class() as session:
            try:
                album = (
                    session.query(AlbumEntity).filter(AlbumEntity.id == album_id).first()
                )
                if album:
                    album.title = updated_album.title
                    album.artist = updated_album.artist
                    album.year = updated_album.year
                    album.genres = updated_album.genres
                    album.styles = updated_album.styles
                    album.labels = updated_album.labels
                    album.country = updated_album.country
                    album.tracklist = updated_album.tracklist
                    album.credits = updated_album.credits
                    album.external_urls = updated_album.external_urls
                    album.external_ids = updated_album.external_ids
                    session.add(album)
                    session.commit()
                    session.refresh(album)
                return album
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error updating album: {e}")
                raise AlbumUpdateError("Failed to update album") from e
