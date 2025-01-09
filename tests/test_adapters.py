from typing import Any

import pytest
from pydantic import ValidationError

from localllm.domain.multimedia import Album, Track
from localllm.infra.spi.web.adapters import DiscogsAlbumAdapter, SpotifyAlbumAdapter


@pytest.fixture
def valid_discogs_metadata() -> dict[str, Any]:
    return {
        "country": "Netherlands",
        "year": "2000",
        "format": ["CD", "Album"],
        "label": [
            "Transmission Records",
            "Transmission Records",
            "Transmission Records",
            "The Electric Castle",
            "RS29",
            "The Dungeon",
            "House Of Music Studios",
            "Crazy Cat Studio, Hamburg",
            "The Walden West Recorder",
            "Ninth Street Studios",
            "Studio Triade",
            "Thin Ice Studios",
            "Sound Factory, Soest",
            "RS29",
            "Sony DADC",
        ],
        "type": "release",
        "genre": ["Rock"],
        "style": ["Progressive Metal", "Rock Opera"],
        "id": 575009,
        "barcode": [
            "8712488993867",
            "8 712488 993867",
            "Sony DADC IFPI L554 A0100318454-0101 14 A4",
            "Sony DADC IFPI L554 A0100318454-0101 14 A1",
            "Sony DADC IFPI L554 A0100318454-0101 14 A5",
            "IFPI L554",
            "IFPI 94Z3",
            "IFPI 949B",
            "STEMRA",
        ],
        "user_data": {"in_wantlist": False, "in_collection": False},
        "master_id": 214918,
        "master_url": "https://api.discogs.com/masters/214918",
        "uri": "/release/575009-Ayreon-Universal-Migrator-Part-2-Flight-Of-The-Migrator",
        "catno": "TM-020",
        "title": "Ayreon - Universal Migrator Part 2: Flight Of The Migrator",
        "thumb": "https://i.discogs.com/5doA7LV5UwuqtFS5noRDvAT6IkADU6D1Ekq8f2bw0gU/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTU3NTAw/OS0xMTQ5MzI4MzA4/LmpwZWc.jpeg",
        "cover_image": "https://i.discogs.com/8PhJnX2CEIkgP6YmPwI5aQ3wHtUtaYGtodv3aBpveWE/rs:fit/g:sm/q:90/h:480/w:480/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTU3NTAw/OS0xMTQ5MzI4MzA4/LmpwZWc.jpeg",
        "resource_url": "https://api.discogs.com/releases/575009",
        "community": {"want": 85, "have": 894},
        "format_quantity": 1,
        "formats": [{"name": "CD", "qty": "1", "descriptions": ["Album"]}],
    }

    # return {
    #     "release_id": "123",
    #     "title": "Daft Punk - Random Access Memories",
    #     "year": 2013,
    #     "genres": ["Electronic", "Pop"],
    #     "styles": ["House", "Disco"],
    #     "labels": ["Columbia", "Sony Music"],
    #     "country": "France",
    #     "tracklist": [
    #         {"position": "1", "title": "Give Life Back to Music", "duration": 60},
    #         {"position": "2", "title": "Get Lucky", "duration": 90},
    #     ],
    #     "credits": "Produced by Daft Punk",
    #     "discogs_url": "https://www.discogs.com/release/123",
    # }


@pytest.fixture
def valid_spotify_metadata() -> dict[str, Any]:
    return {
        "album_type": "album",
        "total_tracks": 8,
        "available_markets": [
            "AR",
            "AU",
            "AT",
            "BE",
            "BO",
            "BR",
            "BG",
            "CA",
            "CL",
            "CO",
            "CR",
            "CY",
            "CZ",
            "DK",
            "DO",
            "DE",
            "EC",
            "EE",
            "SV",
            "FI",
            "FR",
            "GR",
            "GT",
            "HN",
            "HK",
            "HU",
            "IS",
            "IE",
            "IT",
            "LV",
            "LT",
            "LU",
            "MY",
            "MT",
            "MX",
            "NL",
            "NZ",
            "NI",
            "NO",
            "PA",
            "PY",
            "PE",
            "PH",
            "PL",
            "PT",
            "SG",
            "SK",
            "ES",
            "SE",
            "CH",
            "TW",
            "TR",
            "UY",
            "US",
            "GB",
            "AD",
            "LI",
            "MC",
            "ID",
            "JP",
            "TH",
            "VN",
            "RO",
            "IL",
            "ZA",
            "SA",
            "AE",
            "BH",
            "QA",
            "OM",
            "KW",
            "EG",
            "MA",
            "DZ",
            "TN",
            "LB",
            "JO",
            "PS",
            "IN",
            "KZ",
            "MD",
            "UA",
            "SI",
            "KR",
            "BD",
            "PK",
            "LK",
            "GH",
            "KE",
            "NG",
            "TZ",
            "UG",
            "AG",
            "AM",
            "BS",
            "BB",
            "BZ",
            "BT",
            "BW",
            "BF",
            "CV",
            "CW",
            "DM",
            "FJ",
            "GM",
            "GE",
            "GD",
            "GW",
            "GY",
            "HT",
            "JM",
            "KI",
            "LS",
            "MW",
            "MV",
            "ML",
            "MH",
            "FM",
            "NA",
            "NR",
            "NE",
            "PW",
            "PG",
            "PR",
            "WS",
            "SM",
            "ST",
            "SN",
            "SC",
            "SL",
            "SB",
            "KN",
            "LC",
            "VC",
            "SR",
            "TL",
            "TO",
            "TT",
            "TV",
            "VU",
            "AZ",
            "BN",
            "BI",
            "KH",
            "CM",
            "TD",
            "KM",
            "GQ",
            "SZ",
            "GA",
            "GN",
            "KG",
            "LA",
            "MO",
            "MR",
            "MN",
            "NP",
            "RW",
            "TG",
            "UZ",
            "BJ",
            "MG",
            "MU",
            "MZ",
            "AO",
            "DJ",
            "ZM",
            "CG",
            "TJ",
            "VE",
            "ET",
        ],
        "external_urls": {"spotify": "https://open.spotify.com/album/7q0sRz2m6J42lSxINl1DPs"},
        "href": "https://api.spotify.com/v1/albums/7q0sRz2m6J42lSxINl1DPs",
        "id": "7q0sRz2m6J42lSxINl1DPs",
        "images": [
            {"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b27326f5ae57a5699ce580d00acb", "width": 640},
            {"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e0226f5ae57a5699ce580d00acb", "width": 300},
            {"height": 64, "url": "https://i.scdn.co/image/ab67616d0000485126f5ae57a5699ce580d00acb", "width": 64},
        ],
        "name": "Twilight in Olympus (Special Edition)",
        "release_date": "1998",
        "release_date_precision": "year",
        "type": "album",
        "uri": "spotify:album:7q0sRz2m6J42lSxINl1DPs",
        "artists": [
            {
                "external_urls": {"spotify": "https://open.spotify.com/artist/4MnZkh4dpNmTMPxkl4Ev5L"},
                "href": "https://api.spotify.com/v1/artists/4MnZkh4dpNmTMPxkl4Ev5L",
                "id": "4MnZkh4dpNmTMPxkl4Ev5L",
                "name": "Symphony X",
                "type": "artist",
                "uri": "spotify:artist:4MnZkh4dpNmTMPxkl4Ev5L",
            }
        ],
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

    title = valid_discogs_metadata["title"].split(" - ")

    assert album.title == title[1]
    assert album.artist == title[0]
    assert str(album.year) == valid_discogs_metadata["year"]
    assert album.genres == valid_discogs_metadata["genre"]
    assert album.styles == valid_discogs_metadata["style"]


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
    assert album.title == valid_spotify_metadata["name"]
    assert album.artist == valid_spotify_metadata["artists"][0]["name"]
    assert str(album.year) == valid_spotify_metadata["release_date"]


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
    assert len(album.tracklist) == 0
