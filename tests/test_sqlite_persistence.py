import pytest
from sqlalchemy.orm import sessionmaker

from localllm.infra.spi.persistence.repository.databases import (
    AlbumNotFoundError,
    AlbumSaveError,
)
from localllm.infra.spi.persistence.repository.models import AlbumEntity, TrackEntity


@pytest.fixture()
def prepare_database(repository, albums):
    # Given multiple albums to save
    # Given an album to save
    session_class = sessionmaker(repository._engine)
    with session_class() as session:
        for album in albums:
            entity = AlbumEntity(
                id=None,  # Assuming the ID is auto-generated
                album_id=album.album_id,
                title=album.title,
                artist=album.artist,
                year=album.year,
                genres=album.genres,
                styles=album.styles,
                labels=album.labels,
                country=album.country,
                tracklist=[
                    TrackEntity(
                        id=None,  # Assuming the ID is auto-generated
                        position=track.position,
                        title=track.title,
                        duration=track.duration,
                        album_id=None,  # This will be set when the album is saved
                    )
                    for track in album.tracklist
                ],
                credits=album.credits,
                external_urls=album.external_urls,
                external_ids=album.external_ids,
            )

            session.add(entity)
            session.commit()

    yield


def test_create_album_with_album_domain_model_should_save_it_in_database(repository, enriched_album):
    # Given an album to save

    # When saving the album
    repository.create_album(enriched_album)

    # Then the album should be saved in the database
    Session = sessionmaker(bind=repository._engine)
    with Session() as s:
        saved_album = s.query(AlbumEntity).one_or_none()

        assert saved_album is not None
        assert saved_album.album_id == "1234"
        assert saved_album.title == "Album Title"
        assert saved_album.artist == "Artist Name"
        assert saved_album.year == 2021
        assert saved_album.genres == '["Rock", "Pop"]'
        assert saved_album.styles == '["Indie", "Alternative"]'
        assert saved_album.labels == '["Label 1", "Label 2"]'
        assert saved_album.country == "US"
        assert saved_album.credits == "Producer Name"
        assert saved_album.external_urls == '{"spotify": "https://open.spotify.com/album/1234"}'
        assert saved_album.external_ids == '{"spotify": "1234"}'


def test_create_album_with_already_exist_album_should_raise_error(repository, prepare_database, album):
    # Given an album to save
    # When saving the album
    with pytest.raises(AlbumSaveError):
        repository.create_album(album)


def test_get_number_albums_should_return_0_when_database_is_empty(repository):
    # When getting the number of albums
    number_albums = repository.get_number_albums()

    # Then the number of albums should be 0
    assert number_albums == 0


def test_get_number_albums_should_return_right_number_when_database_is_not_empty(repository, prepare_database):
    # When getting the number of albums
    number_albums = repository.get_number_albums()

    # Then the number of albums should be 2
    assert number_albums == 3


def test_get_albums_should_return_empty_list_when_database_is_empty(repository):
    # When retrieving all albums
    albums = repository.get_albums()

    # Then the list of albums should be empty
    assert albums == []


def test_get_albums_should_return_all_albums(repository, prepare_database):
    # Given multiple albums to save
    # When retrieving all albums
    albums = repository.get_albums()

    # Then the list of albums should contain both albums
    assert len(albums) == 3
    assert albums[0].album_id == "1234"
    assert albums[1].album_id == "5678"
    assert albums[2].album_id == "9876"
    assert albums[0].title == "Album Title"
    assert albums[1].title == "Album Title"
    assert albums[2].title == "Another Title"


def test_get_albums_by_id_should_return_album_when_id_exists_in_database(repository, prepare_database):
    # Given multiple albums to save
    # When retrieving album id
    album = repository.get_album_by_id("1234")

    # Then the album should be the correct one
    assert album is not None
    assert album.album_id == "1234"
    assert album.title == "Album Title"


def test_get_albums_by_id_should_raise_error_when_id_do_not_exist_in_database(repository, prepare_database):
    # Given multiple albums to save
    # When retrieving album id
    # Then the album should be None
    with pytest.raises(AlbumNotFoundError):
        repository.get_album_by_id("3421")


def test_search_albums_by_title_should_return_albums_when_albums_exists_in_database(repository, prepare_database):
    # Given multiple albums to save
    # When retrieving album id
    albums = repository.search_albums("Album Title")

    # Then the album should be the correct one
    assert albums is not None
    assert isinstance(albums, list)
    assert len(albums) == 2
    assert albums[0].album_id == "1234"
    assert albums[1].album_id == "5678"
    assert albums[0].title == "Album Title"
    assert albums[1].title == "Album Title"


def test_search_albums_by_title_should_return_empty_list_when_albums_do_not_exist_in_database(
    repository, prepare_database
):
    # Given multiple albums to save
    # When retrieving album id
    albums = repository.search_albums("Non existing Album")

    # Then the album should be the correct one
    assert albums is not None
    assert isinstance(albums, list)
    assert len(albums) == 0


def test_search_albums_by_artist_should_return_albums_when_albums_exists_in_database(repository, prepare_database):
    # Given multiple albums to save
    # When retrieving album id
    albums = repository.search_albums("Another Artist")

    # Then the album should be the correct one
    assert albums is not None
    assert isinstance(albums, list)
    assert len(albums) == 2
    assert albums[0].album_id == "5678"
    assert albums[0].title == "Album Title"
    assert albums[0].artist == "Another Artist"
    assert albums[1].album_id == "9876"
    assert albums[1].title == "Another Title"
    assert albums[1].artist == "Another Artist"


def test_search_albums_by_artist_should_return_no_albums_when_albums_does_not_exists_in_database(
    repository, prepare_database
):
    # Given multiple albums to save
    # When retrieving album id
    albums = repository.search_albums("Non Existing Artist")

    # Then the album should be the correct one
    assert albums is not None
    assert isinstance(albums, list)
    assert len(albums) == 0


def test_search_albums_by_year_should_return_albums_when_albums_exists_in_database(repository, prepare_database):
    # Given multiple albums to save
    # When retrieving album id
    albums = repository.search_albums(2022)

    # Then the album should be the correct one
    assert albums is not None
    assert isinstance(albums, list)
    assert len(albums) == 2
    assert albums[0].album_id == "5678"
    assert albums[0].title == "Album Title"
    assert albums[0].artist == "Another Artist"
    assert albums[1].album_id == "9876"
    assert albums[1].title == "Another Title"
    assert albums[1].artist == "Another Artist"


def test_search_albums_by_year_should_return_no_albums_when_albums_does_not_exists_in_database(
    repository, prepare_database
):
    # Given multiple albums to save
    # When retrieving album id
    albums = repository.search_albums(1990)

    # Then the album should be the correct one
    assert albums is not None
    assert isinstance(albums, list)
    assert len(albums) == 0
