import structlog
from langchain_core.embeddings import Embeddings
from qdrant_client.models import Distance

from localllm.application.use_cases.interfaces import IndexAlbumUseCase
from localllm.domain.multimedia import Album
from localllm.infra.spi.persistence.repository.vectors import QdrantAlbumRepository

DEFAULT_VECTOR_SIZE = 384
logger = structlog.getLogger()


class QdrantIndexAlbums(IndexAlbumUseCase):
    def __init__(
        self,
        database_url: str,
        collection_name: str,
        embeddings: Embeddings = None,
        vector_size: int = DEFAULT_VECTOR_SIZE,
        distance: Distance = Distance.COSINE,
    ):
        self.repository = QdrantAlbumRepository(
            database_url=database_url,
            collection_name=collection_name,
            embeddings=embeddings,
            vector_size=vector_size,
            distance=distance,
        )
        self.repository.initialize()

    def index_albums(self, albums: list[Album]) -> list[Album]:
        for album in albums:
            logger.info(f"Indexing album to vector store - {album.album_id} / {album.title} by {album.artist}")
            entity_id, album = self.repository.index_album(album)
            logger.info(f"Album with album_id {album.album_id} stored into repository with id {entity_id}")

        logger.info("All albums indexed in repository")
        return albums

    def search_albums(self, query: str, top_k: int = 5) -> list[Album]:
        logger.info(f"Searching for albums with query {query}")
        return self.repository.search_albums(query, top_k)
