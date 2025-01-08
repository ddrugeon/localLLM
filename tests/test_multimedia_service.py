from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from localllm.application.services.service import MultimediaIngesterService


@pytest.fixture
def mock_fetcher(albums):
    fetcher = Mock()
    fetcher.read.return_value = albums
    return fetcher


@pytest.fixture
def mock_enricher():
    enricher = AsyncMock()
    enricher.get_album_metadata = AsyncMock()
    return enricher


@pytest.fixture
def mock_repository():
    repository = Mock()
    repository.create_album = AsyncMock()
    return repository


@pytest.fixture
def service(mock_fetcher, mock_enricher, mock_repository):
    return MultimediaIngesterService(fetcher=mock_fetcher, enrichers=[mock_enricher], repository=mock_repository)


def test_load_albums_with_no_fetcher_should_return_empty_array():
    service = MultimediaIngesterService(fetcher=None)
    albums = service.load_albums(Path("dummy_path"))
    assert len(albums) == 0


def test_load_albums_with_fetcher_should_return_album_list(mock_fetcher):
    service = MultimediaIngesterService(fetcher=mock_fetcher)
    albums = service.load_albums(Path("dummy_path"))
    assert len(albums) == 3
    assert albums[0].artist == "Artist Name"
    assert albums[0].title == "Paint in the Sky"
    assert albums[1].artist == "Another Artist"
    assert albums[1].title == "Echoes of the see"
    assert albums[2].artist == "Another Artist"
    assert albums[2].title == "Echoes of the Forest"


def test_load_albums_when_file_not_found_should_raise_exception():
    mock_fetcher = Mock()
    mock_fetcher.read.side_effect = FileNotFoundError("File not found")
    service = MultimediaIngesterService(fetcher=mock_fetcher)

    with pytest.raises(FileNotFoundError):
        service.load_albums(Path("non_existent_file.json"))


@pytest.mark.anyio
async def test_enrich_album_success(mock_enricher, enriched_albums):
    album = enriched_albums[0]
    mock_enricher.get_album_metadata.return_value = album
    service = MultimediaIngesterService(fetcher=None, enrichers=[mock_enricher], repository=None)
    enriched_album = await service._enrich_album(album)

    assert enriched_album.genres == ["Rock", "Pop"]
    assert enriched_album.labels == ["Label 1", "Label 2"]


@pytest.mark.anyio
async def test_enrich_album_no_metadata(mock_enricher, album):
    mock_enricher.get_album_metadata.return_value = None
    service = MultimediaIngesterService(fetcher=None, enrichers=[mock_enricher], repository=None)
    enriched_album = await service._enrich_album(album)

    assert enriched_album.album_id == "1234"
    assert enriched_album.artist == "Artist Name"
    assert enriched_album.genres == []


@pytest.mark.asyncio
async def test_save_album_with_repository(service, album):
    service.repository.create_album = Mock(return_value=album)

    saved_album = await service._save_album(album)

    assert saved_album == album
    service.repository.create_album.assert_called_once_with(album)


@pytest.mark.asyncio
async def test_save_album_without_repository_should_log_it(album):
    with patch("localllm.application.services.service.logger") as logger_mock:
        service = MultimediaIngesterService()
        saved_album = await service._save_album(album)

        assert saved_album == album
        logger_mock.info.assert_any_call("No repository configured, skipping save")


@pytest.mark.asyncio
async def test_save_albums_without_enrichment(service, album):
    service.repository.create_album = AsyncMock(return_value=album)
    albums = [album]
    saved_albums = await service.save_albums(albums, enrich_album=False)
    assert len(saved_albums) == 1
    assert saved_albums[0].album_id == album.album_id
    assert saved_albums[0].title == album.title
    assert saved_albums[0].artist == album.artist
    service.repository.create_album.assert_called_once_with(album)


@pytest.mark.asyncio
async def test_save_albums_with_enrichment(service, album, enriched_album):
    service.repository.create_album = AsyncMock(return_value=enriched_album)
    service._enrich_album = AsyncMock(return_value=enriched_album)
    albums = [album]
    saved_albums = await service.save_albums(albums, enrich_album=True)
    assert len(saved_albums) == 1
    assert saved_albums[0].album_id == enriched_album.album_id
    assert saved_albums[0].title == enriched_album.title
    assert saved_albums[0].artist == enriched_album.artist
    assert saved_albums[0].genres == enriched_album.genres
    service._enrich_album.assert_called_once_with(album)
    service.repository.create_album.assert_called_once_with(enriched_album)


@pytest.mark.asyncio
async def test_save_albums_enrichment_error(service, album):
    service.repository.create_album = AsyncMock(return_value=album)
    service._enrich_album = AsyncMock(side_effect=Exception("Enrichment error"))
    albums = [album]
    saved_albums = await service.save_albums(albums, enrich_album=True)
    assert len(saved_albums) == 1
    assert saved_albums[0] == album
    service._enrich_album.assert_called_once_with(album)
    service.repository.create_album.assert_called_once_with(album)


@pytest.mark.asyncio
async def test_save_albums_save_error(service, album):
    service.repository.create_album = AsyncMock(side_effect=Exception("Save error"))
    albums = [album]
    saved_albums = await service.save_albums(albums, enrich_album=False)
    assert len(saved_albums) == 1
    assert saved_albums[0] == album
    service.repository.create_album.assert_called_once_with(album)
