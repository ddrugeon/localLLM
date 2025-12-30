# tests/test_multimedia_service.py
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from localllm.application.services.service import MultimediaIngesterService


@pytest.fixture
def mock_load_albums_use_case():
    return Mock()


@pytest.fixture
def mock_enrich_album_use_case():
    return AsyncMock()


@pytest.fixture
def mock_store_albums_use_case():
    return AsyncMock()


@pytest.fixture
def mock_index_albums_use_case():
    return Mock()


@pytest.fixture
def mock_file_storage_album_use_case():
    return Mock()


@pytest.fixture
def service(
    mock_load_albums_use_case,
    mock_enrich_album_use_case,
    mock_store_albums_use_case,
    mock_index_albums_use_case,
    mock_file_storage_album_use_case,
):
    return MultimediaIngesterService(
        load_albums_use_case=mock_load_albums_use_case,
        enrich_album_use_case=mock_enrich_album_use_case,
        store_albums_use_case=mock_store_albums_use_case,
        index_albums_use_case=mock_index_albums_use_case,
        file_storage_album_use_case=mock_file_storage_album_use_case,
    )


def test_load_albums(service, album, mock_load_albums_use_case):
    album_file_path = Path("/path/to/albums")
    mock_load_albums_use_case.load_albums.return_value = [album]

    loaded_albums = service.load_albums(album_file_path)

    mock_load_albums_use_case.load_albums.assert_called_once_with(file_path=album_file_path)
    assert loaded_albums == [album]


@pytest.mark.asyncio
async def test_enrich_albums(service, albums, mock_enrich_album_use_case):
    mock_enrich_album_use_case.enrich_albums.return_value = albums

    enriched_albums = await service.enrich_albums(albums)

    mock_enrich_album_use_case.enrich_albums.assert_called_once_with(albums)
    assert enriched_albums == albums


@pytest.mark.asyncio
async def test_store_albums(service, albums, mock_store_albums_use_case):
    mock_store_albums_use_case.store_albums.return_value = albums

    await service.store_albums(albums)

    mock_store_albums_use_case.store_albums.assert_called_once_with(albums)


def test_save_albums(service, album, mock_file_storage_album_use_case):
    albums = [album]
    path = Path("/path/to/save")

    service.save_albums(albums, path)

    mock_file_storage_album_use_case.persist.assert_called_once_with(albums, path)


def test_index_albums(service, album, mock_index_albums_use_case):
    albums = [album]
    mock_index_albums_use_case.index_albums.return_value = albums

    indexed_albums = service.index_albums(albums)

    mock_index_albums_use_case.index_albums.assert_called_once_with(albums)
    assert indexed_albums == albums


def test_search_albums(service, album, mock_index_albums_use_case):
    query = "test"
    top_k = 5
    albums = [album]
    mock_index_albums_use_case.search_albums.return_value = albums

    search_results = service.search_albums(query, top_k)

    mock_index_albums_use_case.search_albums.assert_called_once_with(query, top_k=top_k)
    assert search_results == albums
