from pathlib import Path
from unittest.mock import Mock

import pytest

from localllm.application.services.service import MultimediaService
from localllm.domain.multimedia import Album


@pytest.fixture
def mock_fetcher():
    fetcher = Mock()
    fetcher.read.return_value = [
        Album(artist="Artist", title="Title", album_id="123", year=2024)
    ]
    return fetcher


@pytest.fixture
def mock_enricher():
    enricher = Mock()
    enricher.get_album_metadata.return_value = {
        "album": "Title",
        "artist": "Artist",
        "year": 2024,
        "genres": ["Rock"],
        "styles": ["Pop rock"],
        "labels": ["Label"],
        "country": ["France"],
        "tracklist": [
            {
                "position": "01",
                "title": "My first song",
                "duration": "3:45",
            }
        ],
    }
    return enricher


def test_load_albums(mock_fetcher):
    service = MultimediaService(fetcher=mock_fetcher)
    albums = service.load_albums(Path("dummy_path"))
    assert len(albums) == 1
    assert albums[0].artist == "Artist"
    assert albums[0].title == "Title"


def test_enrich_albums(mock_fetcher, mock_enricher):
    service = MultimediaService(fetcher=mock_fetcher, enricher=mock_enricher)
    albums = service.load_albums(Path("dummy_path"))
    enriched_albums = service.enrich_albums(albums)
    assert len(enriched_albums) == 1
    assert enriched_albums[0]["artist"] == "Artist"
    assert enriched_albums[0]["album"] == "Title"
    assert enriched_albums[0]["year"] == 2024
    assert enriched_albums[0]["genres"] == ["Rock"]
    assert enriched_albums[0]["styles"] == ["Pop rock"]
    assert enriched_albums[0]["labels"] == ["Label"]
    assert enriched_albums[0]["country"] == ["France"]
    assert enriched_albums[0]["tracklist"] == [
        {
            "position": "01",
            "title": "My first song",
            "duration": "3:45",
        }
    ]
