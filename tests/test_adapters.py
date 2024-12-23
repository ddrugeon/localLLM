from typing import Any

import pytest
from pydantic import ValidationError

from localllm.domain.multimedia import Album, Track
from localllm.infra.spi.web.adapters import DiscogsAlbumAdapter, SpotifyAlbumAdapter


@pytest.fixture
def valid_discogs_metadata() -> dict[str, Any]:
    return {
        "release_id": "123",
        "title": "Daft Punk - Random Access Memories",
        "year": 2013,
        "genres": ["Electronic", "Pop"],
        "styles": ["House", "Disco"],
        "labels": ["Columbia", "Sony Music"],
        "country": "France",
        "tracklist": [
            {"position": "1", "title": "Give Life Back to Music", "duration": 60},
            {"position": "2", "title": "Get Lucky", "duration": 90},
        ],
        "credits": "Produced by Daft Punk",
        "discogs_url": "https://www.discogs.com/release/123",
    }


@pytest.fixture
def valid_spotify_metadata() -> dict[str, Any]:
    return {
        "album": "Random Access Memories",
        "artist": "Daft Punk",
        "release_date": "2013-05-17",
        "genres": ["Electronic", "French House"],
        "label": "Columbia",
        "popularity": 82,
        "tracks": [
            {"position": 1, "title": "Give Life Back to Music", "duration": "337000"},
            {"position": 2, "title": "Get Lucky", "duration": "367000"},
        ],
        "spotify_url": "https://open.spotify.com/album/123456",
    }


@pytest.fixture
def discogs_adapter() -> DiscogsAlbumAdapter:
    return DiscogsAlbumAdapter()


@pytest.fixture
def spotify_adapter() -> SpotifyAlbumAdapter:
    return SpotifyAlbumAdapter()


def test_valid_track_creation():
    track = Track(position=1, title="Test Track", duration=225)
    assert track.position == 1
    assert track.title == "Test Track"
    assert track.duration == 225


def test_track_without_duration():
    track = Track(position="1", title="Test Track")
    assert track.duration is None


def test_invalid_track_missing_required():
    with pytest.raises(ValidationError):
        Track(position="1")  # Missing title

    with pytest.raises(ValidationError):
        Track(title="Test Track")  # Missing position


def test_valid_album_creation():
    album = Album(album_id="test_123", title="Test Album", artist="Test Artist", year=2023)
    assert album.album_id == "test_123"
    assert album.title == "Test Album"
    assert album.artist == "Test Artist"
    assert album.year == 2023


def test_album_with_optional_fields():
    album = Album(
        album_id="test_123",
        title="Test Album",
        artist="Test Artist",
        year=2023,
        genres=["Rock", "Pop"],
        labels=["Test Label"],
        popularity=75,
    )
    assert len(album.genres) == 2
    assert album.labels == ["Test Label"]
    assert album.popularity == 75


def test_invalid_popularity_validation():
    with pytest.raises(ValidationError):
        Album(
            album_id="test_123",
            title="Test Album",
            artist="Test Artist",
            year=2023,
            popularity=101,  # Supérieur à 100
        )


def test_discogs_valid_conversion(discogs_adapter, valid_discogs_metadata):
    album = discogs_adapter.to_album(valid_discogs_metadata)
    assert album is not None
    assert album.title == "Random Access Memories"
    assert album.artist == "Daft Punk"
    assert album.year == 2013
    assert len(album.tracklist) == 2
    assert album.genres == ["Electronic", "Pop"]
    assert album.styles == ["House", "Disco"]


def test_discogs_missing_required_fields(discogs_adapter):
    incomplete_metadata = {
        "release_id": "123",
        "title": "Test Album",
        # artist and year
    }
    album = discogs_adapter.to_album(incomplete_metadata)
    assert album is None


def test_discogs_empty_metadata(discogs_adapter):
    assert discogs_adapter.to_album({}) is None
    assert discogs_adapter.to_album(None) is None


def test_spotify_valid_conversion(spotify_adapter, valid_spotify_metadata):
    album = spotify_adapter.to_album(valid_spotify_metadata)
    assert album is not None
    assert album.title == "Random Access Memories"
    assert album.artist == "Daft Punk"
    assert album.year == 2013
    assert len(album.tracklist) == 2
    assert album.popularity == 82
    assert "Columbia" in album.labels


def test_release_date_parsing(spotify_adapter, valid_spotify_metadata):
    metadata = valid_spotify_metadata.copy()

    # Only year
    metadata["release_date"] = "2013"
    album = spotify_adapter.to_album(metadata)
    assert album.year == 2013

    # Invalid date
    metadata["release_date"] = "invalid"
    album = spotify_adapter.to_album(metadata)
    assert album.year == 0


def test_spotify_empty_metadata(spotify_adapter):
    assert spotify_adapter.to_album({}) is None
    assert spotify_adapter.to_album(None) is None


def test_track_conversion(spotify_adapter, valid_spotify_metadata):
    album = spotify_adapter.to_album(valid_spotify_metadata)
    assert len(album.tracklist) == 2
    track = album.tracklist[0]
    assert track.position == 1
    assert track.title == "Give Life Back to Music"
    assert track.duration == 337000
