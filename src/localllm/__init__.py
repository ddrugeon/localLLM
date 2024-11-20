from pathlib import Path

import structlog

from localllm.application.services.service import MultimediaService
from localllm.config import Settings
from localllm.infra.outputs.enrichers import DiscogsAlbumEnricher
from localllm.infra.outputs.fetchers import LocalFileJSONReader

logger = structlog.getLogger()


def main() -> None:
    settings: Settings = Settings()
    logger.info(f"Settings loaded: {settings.model_dump()}")

    source_file = Path(settings.document_folder, "albums.json")
    fetcher = LocalFileJSONReader()
    enricher = DiscogsAlbumEnricher(
        discogs_token=settings.discogs_user_token.get_secret_value()
    )

    service = MultimediaService(fetcher=fetcher, enricher=enricher)
    albums = service.load_albums(source_file)

    logger.info("Albums loaded")
    logger.info("Enriching albums")

    logger.info(service.enrich_albums(albums))
