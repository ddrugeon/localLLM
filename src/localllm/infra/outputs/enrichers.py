from typing import Optional

from localllm.domain.ports.enrichers import AlbumEnricher

import structlog
import discogs_client

logger = structlog.getLogger()


class DiscogsAlbumEnricher(AlbumEnricher):
    """Enriches album metadata using Discogs API."""

    def __init__(self, discogs_token: str):
        self.discogs = discogs_client.Client("Localllm/0.1", user_token=discogs_token)

    def get_album_metadata(self, artist: str, album: str) -> Optional[dict]:
        """Retrieves album metadata from Discogs."""
        logger.debug(f"Retrieving metadata for {album} by {artist} on Discogs")

        search_results = self.discogs.search(f'{artist} {album}', type='release')

        if not search_results:
            logger.warning(f"No results found for {album} by {artist}")
            return None

        release = search_results[0]

        return {
            "release_id": release.id,
            "album": release.title,
            "artist": release.artists[0].name,
            "credits": release.artists_sort,
            "year": release.year,
            "genres": release.genres if hasattr(release, "genres") else [],
            "styles": release.styles if hasattr(release, "styles") else [],
            "labels": [label.name for label in release.labels],
            "country": release.country,
            "tracklist": [{"position": track.position, "title": track.title, "duration": track.duration} for track in release.tracklist],
            "discogs_url": release.url
        }