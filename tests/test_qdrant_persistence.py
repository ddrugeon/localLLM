from uuid import uuid4

import pytest
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client.models import Distance

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
        distance=Distance.COSINE
    )
    repository.initialize()
    yield repository
    repository.close()


def test_index_album_with_album_domain_model_should_save_it_in_database(qdrant_repository, enriched_album):
    album_id, created_album = qdrant_repository.index_album(enriched_album)

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
