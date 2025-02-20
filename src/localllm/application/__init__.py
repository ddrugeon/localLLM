from pathlib import Path

import structlog
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client.models import Distance

from localllm.application.services.service import MultimediaIngesterService
from localllm.application.use_cases.enrich_albums import EnrichAlbums
from localllm.application.use_cases.index_albums import QdrantIndexAlbums
from localllm.application.use_cases.load_albums import LoadAlbums
from localllm.application.use_cases.store_albums import DatabaseStoreAlbums
from localllm.config import Settings
from localllm.domain.multimedia import Album
from localllm.infra.spi.persistence.file.fetchers import LocalFileJSONReader
from localllm.infra.spi.persistence.repository.databases import DatabaseAlbumPersistence
from localllm.infra.spi.web.enrichers import DiscogsAlbumEnricher, SpotifyAlbumEnricher

logger = structlog.getLogger(__name__)


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
        db_repository = DatabaseAlbumPersistence(db_url=settings.database_model_url)

        embeddings = FastEmbedEmbeddings()

        self.__service = MultimediaIngesterService(
            load_albums_use_case=LoadAlbums(fetcher),
            enrich_album_use_case=EnrichAlbums(enrichers),
            store_albums_use_case=DatabaseStoreAlbums(db_repository),
            index_albums_use_case=QdrantIndexAlbums(
                database_url=settings.vector_model_url,
                collection_name="albums",
                embeddings=embeddings,
                vector_size=len(embeddings.embed_query("test")),
                distance=Distance.COSINE,
            ),
        )

    async def ingest_albums(self, enrich_album: bool = False) -> None:
        logger.debug("Loading albums")
        albums = self.__service.load_albums(self.__source_file)
        logger.debug("Albums loaded")

        logger.debug("Processing albums")
        await self.__service.save_albums(albums, enrich_album=enrich_album)
        logger.debug("Albums processed")

    async def index_albums(self) -> None:
        logger.debug("Loading albums")
        albums = self.__service.load_albums(self.__source_file)
        logger.debug("Albums loaded")

        logger.debug("Processing albums")
        self.__service.index_albums(albums)
        logger.debug("Albums processed")

    async def search_albums(self, query: str) -> list[Album]:
        logger.debug(f"Searching albums with this query: {query}")
        results = self.__service.search_albums(query)
        logger.debug(f"Number of results: {len(results)}")
        logger.debug(f"Search results: {results}")
        return results
