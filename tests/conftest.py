import asyncio

import pytest

from localllm import DatabaseAlbumPersistence
from localllm.domain.multimedia import Album, Track

TEST_DATABASE_URL = "sqlite:///:memory:"  # In-memory database for testing


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def album():
    yield Album(
        album_id="1234",
        title="Album Title",
        artist="Artist Name",
        year=2021,
    )


@pytest.fixture()
def albums():
    yield [
        Album(
            album_id="1234",
            title="Album Title",
            artist="Artist Name",
            year=2021,
        ),
        Album(
            album_id="5678",
            title="Album Title",
            artist="Another Artist",
            year=2022,
        ),
        Album(
            album_id="9876",
            title="Another Title",
            artist="Another Artist",
            year=2022,
        ),
    ]


@pytest.fixture()
def enriched_albums():
    yield [
        Album(
            album_id="1234",
            title="Album Title",
            artist="Artist Name",
            year=2021,
            genres=["Rock", "Pop"],
            styles=["Indie", "Alternative"],
            labels=["Label 1", "Label 2"],
            country="US",
            tracklist=[
                Track(position=1, title="Track 1", duration=180),
                Track(position=2, title="Track 2", duration=210),
            ],
            credits="Producer Name",
            external_urls={"spotify": "https://open.spotify.com/album/1234"},
            external_ids={"spotify": "1234"},
        ),
        Album(
            album_id="5678",
            title="Album Title",
            artist="Another Artist",
            year=2022,
            genres=["Pop", "Electronic"],
            styles=["Synth-pop", "Disco"],
            labels=["Label 3", "Label 4"],
            country="UK",
            tracklist=[
                Track(position=1, title="Track 1", duration=200),
                Track(position=2, title="Track 2", duration=190),
            ],
            credits="Another Producer",
            external_urls={"spotify": "https://open.spotify.com/album/5678"},
            external_ids={"spotify": "5678"},
        ),
        Album(
            album_id="9876",
            title="Another Title",
            artist="Another Artist",
            year=2022,
            genres=["Pop", "Rock"],
            styles=["K-pop", "Funk"],
            labels=["Label 3", "Label 4"],
            country="UK",
            tracklist=[
                Track(position=1, title="Track 1", duration=200),
                Track(position=2, title="Track 2", duration=190),
            ],
            credits="Another Producer",
            external_urls={"spotify": "https://open.spotify.com/album/9876"},
            external_ids={"spotify": "9876"},
        ),
    ]


# Fixture for the repository with the in-memory database
@pytest.fixture
def repository():
    repository = DatabaseAlbumPersistence(db_url=TEST_DATABASE_URL)
    repository.initialize()
    yield repository
