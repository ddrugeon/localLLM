from uuid import uuid4

import pytest
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client.models import PointStruct

from localllm.infra.spi.persistence.repository.databases import AlbumNotFoundError
from localllm.infra.spi.persistence.repository.vectors import QdrantAlbumRepository, _album_to_document


@pytest.fixture()
def database_url():
    return ":memory:"


@pytest.fixture()
def embeddings():
    return FastEmbedEmbeddings()


@pytest.fixture(scope="function")
def qdrant_repository(database_url, embeddings):
    repository = QdrantAlbumRepository(
        database_url=database_url,
        collection_name="test_collection",
        embeddings=embeddings,
        vector_size=384,
    )
    repository.initialize()
    yield repository
    repository.close()


def test_create_album_with_album_domain_model_should_save_it_in_database(qdrant_repository, enriched_album):
    album_id, created_album = qdrant_repository.create_album(enriched_album)

    assert album_id is not None
    assert created_album is not None
    assert created_album == enriched_album

    points = qdrant_repository.qdrant_client.retrieve(
        collection_name=qdrant_repository.collection_name, ids=[str(album_id)], with_payload=True
    )

    assert len(points) == 1
    stored_point = points[0]
    metadata = stored_point.payload["metadata"]
    assert metadata["album_id"] == enriched_album.album_id
    assert metadata["title"] == enriched_album.title
    assert metadata["artist"] == enriched_album.artist
    assert metadata["year"] == enriched_album.year
    assert metadata["genres"] == enriched_album.genres


def test_get_number_albums_should_return_0_when_database_is_empty(qdrant_repository):
    # When getting the number of albums
    number_albums = qdrant_repository.get_number_albums()

    # Then the number of albums should be 0
    assert number_albums == 0


def test_get_albums_with_empty_database_should_return_empty_list(qdrant_repository):
    albums = qdrant_repository.get_albums()
    assert isinstance(albums, list)
    assert len(albums) == 0
    assert qdrant_repository.get_number_albums() == 0


def test_get_albums_should_return_all_albums_in_database(embeddings, qdrant_repository, enriched_album):
    # Given an album to save
    vector = embeddings.embed_query(
        f"{enriched_album.title} {enriched_album.artist} {enriched_album.year} {' '.join(enriched_album.genres)}"
    )

    # Manually insert the album into the repository's internal storage
    qdrant_repository.qdrant_client.upsert(
        collection_name=qdrant_repository.collection_name,
        points=[
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "album_id": enriched_album.album_id,
                    "title": enriched_album.title,
                    "artist": enriched_album.artist,
                    "year": enriched_album.year,
                    "genres": enriched_album.genres,
                },
            )
        ],
    )

    # When getting all albums
    albums = qdrant_repository.get_albums()

    # Then the album should be returned
    assert len(albums) == 1
    assert albums[0].album_id == enriched_album.album_id
    assert albums[0].title == enriched_album.title
    assert albums[0].artist == enriched_album.artist
    assert albums[0].year == enriched_album.year
    assert albums[0].genres == enriched_album.genres


def test_get_album_by_id_should_return_album_when_id_exists_in_database(embeddings, qdrant_repository, enriched_album):
    # Given an album to save
    vector = embeddings.embed_query(
        f"{enriched_album.album_id} "
        f"{enriched_album.title} "
        f"{enriched_album.artist} "
        f"{enriched_album.year} "
        f"{' '.join(enriched_album.genres)}"
    )

    # Manually insert the album into the repository's internal storage
    qdrant_repository.qdrant_client.upsert(
        collection_name=qdrant_repository.collection_name,
        points=[
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "album_id": enriched_album.album_id,
                    "title": enriched_album.title,
                    "artist": enriched_album.artist,
                    "year": enriched_album.year,
                    "genres": enriched_album.genres,
                },
            )
        ],
    )

    # When getting the album by ID
    album = qdrant_repository.get_album_by_id(enriched_album.album_id)

    # Then the album should be returned
    assert album is not None
    assert album.album_id == enriched_album.album_id
    assert album.title == enriched_album.title
    assert album.artist == enriched_album.artist
    assert album.year == enriched_album.year
    assert album.genres == enriched_album.genres


def test_get_album_by_id_should_return_none_when_id_does_not_exist_in_database(qdrant_repository):
    # Given an album ID that does not exist in the database
    album_id = "non-existent-album-id"

    # When getting the album by ID
    with pytest.raises(AlbumNotFoundError):
        qdrant_repository.get_album_by_id(album_id)


def test_search_albums_should_return_albums_when_query_matches_title_in_database(embeddings, qdrant_repository, albums):
    # Given an album to save
    # Manually insert the album into the repository's internal storage
    qdrant_repository.langchain_qdrant.add_documents(
        documents=[_album_to_document(current_album) for current_album in albums],
        ids=[str(uuid4().hex) for idx, _ in enumerate(albums)],
    )

    # When searching for albums by title
    searched_albums = qdrant_repository.search_albums("Echoes")
    expected_albums = [albums[1], albums[2]]
    # Then the album should be returned
    assert len(searched_albums) == 2
    for idx, album in enumerate(searched_albums):
        assert album.album_id == expected_albums[idx].album_id
        assert album.title == expected_albums[idx].title
        assert album.artist == expected_albums[idx].artist
        assert album.year == expected_albums[idx].year
        assert album.genres == expected_albums[idx].genres


def test_search_albums_should_return_albums_when_query_does_no_match_title_in_database(
    embeddings, qdrant_repository, albums
):
    # Given an album to save
    # Manually insert the album into the repository's internal storage
    qdrant_repository.langchain_qdrant.add_documents(
        documents=[_album_to_document(current_album) for current_album in albums],
        ids=[str(uuid4().hex) for idx, _ in enumerate(albums)],
    )

    # When searching for albums by title
    searched_albums = qdrant_repository.search_albums("Les Miserables")

    # Then the album should be returned
    assert len(searched_albums) == 0


def test_search_albums_should_return_empty_list_when_no_albums_in_database(qdrant_repository):
    # Given an empty database
    query = "search query"

    # When searching for albums
    albums = qdrant_repository.search_albums(query)

    # Then no albums should be returned
    assert isinstance(albums, list)
    assert len(albums) == 0
