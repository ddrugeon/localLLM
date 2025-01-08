import asyncio

import structlog

from localllm.application.use_cases.interfaces import EnrichAlbumUseCase
from localllm.domain.multimedia import Album
from localllm.domain.ports.enrichers import AlbumEnricher

logger = structlog.getLogger(__name__)


class EnrichAlbums(EnrichAlbumUseCase):
    def __init__(self, enrichers: list[AlbumEnricher]):
        self.enrichers = enrichers

    async def enrich_albums(self, albums: list[Album]) -> list[Album]:
        """
        Enrich albums with additional information from an external source.

        :param albums: list of Album to enrich.
        :return: list of Album enriched with new metadata from external sources.
        """

        async def enrich_album(album: Album) -> Album:
            logger.info(f"Enriching album: {album.title} by {album.artist}")
            metadata_tasks = [enricher.get_album_metadata(album.artist, album.title) for enricher in self.enrichers]
            results = await asyncio.gather(*metadata_tasks)

            combined_metadata = album.model_dump()
            for metadata in results:
                if metadata:
                    combined_metadata.update({k: v for k, v in metadata.dict().items() if v is not None})

            return Album(**combined_metadata)

        tasks = [enrich_album(album) for album in albums]
        enriched_albums = await asyncio.gather(*tasks, return_exceptions=True)
        return [album for album in enriched_albums if isinstance(album, Album)]
