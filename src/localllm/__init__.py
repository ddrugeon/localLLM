import asyncio
from pathlib import Path

import structlog

from localllm.application.services.service import MultimediaService
from localllm.config import Settings
from localllm.infra.spi.persistence.file.fetchers import LocalFileJSONReader
from localllm.infra.spi.persistence.repository.databases import DatabaseAlbumPersistence
from localllm.infra.spi.web.enrichers import DiscogsAlbumEnricher, SpotifyAlbumEnricher

logger = structlog.getLogger()


class Application:
    def __init__(self):
        self.__setup()

    def __setup(self) -> None:
        settings: Settings = Settings()
        logger.debug(f"Settings loaded: {settings.model_dump()}")

        logger.debug("Initializing multimedia assistant")
        self.__source_file = Path(settings.document_folder, "albums.json")
        fetcher = LocalFileJSONReader()
        discogs_enricher = DiscogsAlbumEnricher(discogs_token=settings.discogs_user_token.get_secret_value())
        spotify_enricher = SpotifyAlbumEnricher(
            client_id=settings.spotify_client_id.get_secret_value(),
            client_secret=settings.spotify_client_secret.get_secret_value(),
        )

        enrichers = [discogs_enricher, spotify_enricher]
        repository = DatabaseAlbumPersistence(db_url=settings.database_model_url)

        self.__service = MultimediaService(fetcher=fetcher, enrichers=enrichers, repository=repository)

    async def ingest_albums(self) -> None:
        logger.info("Loading albums")
        albums = self.__service.load_albums(self.__source_file)
        logger.info("Albums loaded")

        logger.info("Processing albums")
        await self.__service.save_albums(albums, enrich_album=False)
        logger.info("Albums processed")


async def application_main() -> None:
    app = Application()
    await app.ingest_albums()


def main() -> None:
    asyncio.run(application_main())


if __name__ == "__main__":
    asyncio.run(application_main())
