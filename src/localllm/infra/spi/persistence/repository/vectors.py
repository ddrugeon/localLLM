from uuid import uuid4

import structlog
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore as QdrantLangChain
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from localllm.domain.multimedia import Album, Track
from localllm.domain.ports.persistence import AlbumVectorRepository

logger = structlog.getLogger()


def _album_to_text(album: Album) -> str:
    return (f"{album.album_id} "
            f"{album.title} "
            f"{album.artist} "
            f"{album.year} "
            f"{' '.join(album.genres)} "
            f"{' '.join(album.styles)} "
            f"{' '.join(album.labels)} "
            f"{album.country} "
            )


def _album_to_document(album: Album) -> Document:
    metadata = {
        "album_id": album.album_id,
        "title": album.title,
        "artist": album.artist,
        "year": album.year,
        "genres": album.genres,
        "styles": album.styles if album.styles else [],
        "labels": album.labels if album.labels else [],
        "country": album.country if album.country else "",
        "tracklist": [track.title for track in album.tracklist] if album.tracklist else [],
        "credits": album.credits if album.credits else "",
        "external_urls": album.external_urls if album.external_urls else {},
        "external_ids": album.external_ids if album.external_ids else {},
    }

    return Document(page_content=_album_to_text(album=album), metadata=metadata)


def _document_to_album(document: Document) -> Album:
    metadata = document.metadata
    return Album(
        album_id=metadata["album_id"],
        title=metadata["title"],
        artist=metadata["artist"],
        year=metadata["year"],
        genres=metadata["genres"] if "genres" in metadata else [],
        styles=metadata["styles"] if "styles" in metadata else [],
        labels=metadata["labels"] if "labels" in metadata else [],
        country=metadata["country"] if "country" in metadata else "",
        tracklist=[Track(title=title) for title in metadata["tracklist"]] if "tracklist" in metadata else [],
        credits=metadata["credits"] if "credits" in metadata else "",
        external_urls=metadata["external_urls"] if "external_urls" in metadata else {},
        external_ids=metadata["external_ids"] if "external_ids" in metadata else {},
    )


class QdrantAlbumRepository(AlbumVectorRepository):
    def __init__(
        self,
        database_url: str,
        collection_name: str,
        embeddings: Embeddings,
        vector_size: int,
        distance: Distance,
    ):
        self.qdrant_client = QdrantClient(location=database_url)
        self.collection_name = collection_name
        self.embeddings = embeddings or FastEmbedEmbeddings()
        self.vector_size = vector_size or len(self.embeddings.embed_query("test"))
        self.distance = distance
        self.text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
        self.langchain_qdrant = None

    def initialize(self) -> None:
        if not self.qdrant_client.collection_exists(self.collection_name):
            logger.info(f"Creating collection {self.collection_name}")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance,
                ),
            )
            logger.info(f"Collection {self.collection_name} created")

        self.langchain_qdrant = QdrantLangChain(
            client=self.qdrant_client, collection_name=self.collection_name, embedding=self.embeddings
        )

    def index_album(self, album: Album) -> (str, Album):
        current_id = uuid4()
        document = _album_to_document(album)

        self.langchain_qdrant.add_documents(documents=[document], ids=[str(current_id)])
        return current_id, album

    def search_albums(self, query: str, top_k: int = 3) -> list[Album]:
        documents = self.langchain_qdrant.search(query=query, k=top_k, search_type="similarity", score_threshold=0.65)
        return [_document_to_album(document) for document in documents]

    def close(self) -> None:
        self.qdrant_client.close()
        self.langchain_qdrant = None
