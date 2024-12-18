import logging

import discogs_client
import spotipy
import structlog
from spotipy.oauth2 import SpotifyClientCredentials
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from localllm.domain.multimedia import Album
from localllm.domain.ports.enrichers import AlbumEnricher
from localllm.infra.spi.web.adapters import DiscogsAlbumAdapter, SpotifyAlbumAdapter

logger = structlog.getLogger()
DISCOGS_USER_AGENT = "Localllm/0.1"
RETRY_MULTIPLIER = 1
RETRY_MIN = 4
RETRY_MAX = 30
RETRY_ATTEMPTS = 5
RATE_LIMIT_STATUS_CODE = "429"
RATE_LIMIT_MESSAGE = "rate limit"


class RateLimitException(Exception):
    """
    Exception raised when an API rate limit is reached.
    """  # noqa: D200

    pass


class DiscogsRateLimitException(RateLimitException):
    """
    Exception raised when the Discogs API rate limit is reached.
    """ # noqa: D200

    pass


class SpotifyRateLimitException(RateLimitException):
    """
    Exception raised when the Spotify API rate limit is reached.
    """ # noqa: D200

    pass


class BaseAlbumEnricher(AlbumEnricher):
    """
    Base class for album enrichers with common functionality.
    """ # noqa: D200

    def _is_rate_limit_exception(self, exception: Exception) -> bool:
        """
        Checks if the given exception is a rate limit exception.

        :param exception: The exception to check.
        :return: True if the exception is a rate limit exception, False otherwise.
        """
        return (
            RATE_LIMIT_STATUS_CODE in str(exception)
            or RATE_LIMIT_MESSAGE in str(exception).lower()
        )


class DiscogsAlbumEnricher(BaseAlbumEnricher):
    def __init__(self, discogs_token: str):
        """
        Initializes the DiscogsAlbumEnricher with the given Discogs token.

        :param discogs_token: The Discogs API token.
        """
        self.discogs = discogs_client.Client(DISCOGS_USER_AGENT, user_token=discogs_token)

    @retry(
        retry=retry_if_exception_type(DiscogsRateLimitException),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN, max=RETRY_MAX),
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        before_sleep=before_sleep_log(logger, log_level=logging.INFO),
        reraise=True,
    )
    async def _search_with_retry(
        self, query: str
    ) -> discogs_client.models.Release | None:
        """
        Searches for a release on Discogs, with rate limit handling.

        :param query: The search query.
        :return: The first search result, or None if no results are found.
        """
        try:
            search_results = self.discogs.search(query, type="release")
            if not search_results:
                return None
            return search_results[0]
        except Exception as e:
            if self._is_rate_limit_exception(e):
                raise DiscogsRateLimitException("Rate limit reached") from e
            raise

    async def get_album_metadata(self, artist: str, album: str) -> Album | None:
        """
        Retrieves album metadata from Discogs.

        :param artist: The artist name.
        :param album: The album name.
        :return: The album metadata, or None if no results are found.
        """
        logger.debug(f"Retrieving metadata for {album} by {artist} on Discogs")
        release = await self._search_with_retry(f"{artist} {album}")
        if not release:
            logger.warning(f"No results found for {album} by {artist}")
            return None
        logger.debug(f"Album data: {release}")
        return DiscogsAlbumAdapter().to_album(metadata=release.data)


class SpotifyAlbumEnricher(BaseAlbumEnricher):
    def __init__(self, client_id: str, client_secret: str):
        """
        Initializes the SpotifyAlbumEnricher with the given Spotify client credentials.

        :param client_id: The Spotify client ID.
        :param client_secret: The Spotify client secret.
        """
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )

    @retry(
        retry=retry_if_exception_type(SpotifyRateLimitException),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN, max=RETRY_MAX),
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        before_sleep=before_sleep_log(logger, log_level=logging.INFO),
        reraise=True,
    )
    async def _search_with_retry(self, query: str) -> dict | None:
        """
        Searches for a release on Spotify, with rate limit handling.

        :param query: The search query.
        :return: The first search result, or None if no results are found.
        """
        try:
            search_results = self.spotify.search(q=query, type="album")
            if not search_results["albums"]["items"]:
                return None
            return search_results["albums"]["items"][0]
        except Exception as e:
            if self._is_rate_limit_exception(e):
                raise SpotifyRateLimitException("Rate limit reached") from e
            raise

    async def get_album_metadata(self, artist: str, album: str) -> Album | None:
        """
        Retrieves album metadata from Spotify.

        :param artist: The artist name.
        :param album: The album name.
        :return: The album metadata, or None if no results are found.
        """
        logger.debug(f"Retrieving metadata for {album} by {artist} on Spotify")
        release = await self._search_with_retry(f"artist:{artist} album:{album}")
        if not release:
            logger.warning(f"No results found for {album} by {artist}")
            return None
        logger.debug(f"Album data: {release}")
        return SpotifyAlbumAdapter().to_album(metadata=release)
