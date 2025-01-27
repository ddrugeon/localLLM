import structlog
from langchain_ollama import OllamaEmbeddings
from qdrant_client.models import Distance

from localllm.application import (
    DatabaseStoreAlbums,
    EnrichAlbums,
    LoadAlbums,
    MultimediaIngesterService,
    QdrantIndexAlbums,
)
from localllm.application.use_cases.store_albums import JSONFileStorageAlbums
from localllm.config import Settings
from localllm.infra.spi.persistence.file.fetchers import LocalFileJSONReader
from localllm.infra.spi.persistence.file.repository import JSONAlbumFileStorage
from localllm.infra.spi.persistence.repository.databases import DatabaseAlbumPersistence
from localllm.infra.spi.web.enrichers import DiscogsAlbumEnricher, SpotifyAlbumEnricher

logger = structlog.getLogger(__name__)


def create_multimedia_service() -> MultimediaIngesterService:
    settings: Settings = Settings()
    logger.debug(f"Settings loaded: {settings.model_dump()}")

    logger.debug("Initializing multimedia assistant")

    fetcher = LocalFileJSONReader()
    discogs_enricher = DiscogsAlbumEnricher(discogs_token=settings.discogs_user_token.get_secret_value())
    spotify_enricher = SpotifyAlbumEnricher(
        client_id=settings.spotify_client_id.get_secret_value(),
        client_secret=settings.spotify_client_secret.get_secret_value(),
    )

    enrichers = [discogs_enricher, spotify_enricher]
    db_repository = DatabaseAlbumPersistence(db_url=settings.database_model_url)
    json_repository = JSONAlbumFileStorage()

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    return MultimediaIngesterService(
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
        file_storage_album_use_case=JSONFileStorageAlbums(json_repository),
    )
