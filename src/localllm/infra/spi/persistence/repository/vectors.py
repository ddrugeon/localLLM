from uuid import uuid4

import structlog
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import Qdrant as QdrantLangChain
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, VectorParams

from localllm.domain.multimedia import Album, Track
from localllm.domain.ports.persistence import AlbumRepository
from localllm.infra.spi.persistence.repository.databases import AlbumNotFoundError

DEFAULT_VECTOR_SIZE = 384
logger = structlog.getLogger()


def _album_to_text(album: Album) -> str:
    return f"{album.album_id} " f"{album.title} " f"{album.artist} " f"{album.year} " f"{' '.join(album.genres)}"


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


class QdrantAlbumRepository(AlbumRepository):
    def __init__(
        self,
        database_url: str,
        collection_name: str,
        embeddings: Embeddings = None,
        vector_size: int = DEFAULT_VECTOR_SIZE,
        distance: Distance = Distance.COSINE,
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
            client=self.qdrant_client, collection_name=self.collection_name, embeddings=self.embeddings
        )

    def create_album(self, album: Album) -> (str, Album):
        current_id = uuid4()
        document = _album_to_document(album)

        self.langchain_qdrant.add_documents(documents=[document], ids=[str(current_id)])
        return current_id, album

    def get_number_albums(self) -> int:
        try:
            collection_info = self.qdrant_client.get_collection(collection_name=self.collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.info(f"Error getting number of albums: {e}")
            return 0

    def get_albums(self) -> list[Album]:
        try:
            # Get all points IDs from collection
            collection_info = self.qdrant_client.get_collection(collection_name=self.collection_name)
            if collection_info.points_count == 0:
                return []

            # Retrieve all points with their payloads
            all_points = self.qdrant_client.scroll(
                collection_name=self.collection_name, with_payload=True, limit=collection_info.points_count
            )[0]  # scroll returns tuple (points, next_page_offset)

            # Process points into albums
            seen_album_ids = set()
            albums = []

            for point in all_points:
                album_id = point.payload["album_id"]
                if album_id not in seen_album_ids:
                    albums.append(
                        Album(
                            album_id=album_id,
                            title=point.payload["title"],
                            artist=point.payload["artist"],
                            year=point.payload["year"],
                            genres=point.payload.get("genres", []),
                            styles=point.payload.get("styles", []),
                            labels=point.payload.get("labels", []),
                            country=point.payload.get("country", ""),
                            tracklist=[Track(title=t) for t in point.payload.get("tracklist", [])],
                            credits=point.payload.get("credits", ""),
                            external_urls=point.payload.get("external_urls", {}),
                            external_ids=point.payload.get("external_ids", {}),
                        )
                    )
                    seen_album_ids.add(album_id)

            return albums

        except Exception as e:
            logger.error(f"Error retrieving albums: {e}")
            return []

    def get_album_by_id(self, album_id: str) -> Album:
        points = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=self.embeddings.embed_query(album_id),
            query_filter=Filter(must=[FieldCondition(key="album_id", match=MatchValue(value=album_id))]),
        )

        if points:
            album_data = points[0].payload
            return _document_to_album(Document(page_content="", metadata=album_data))
        raise AlbumNotFoundError(f"Album with ID {album_id} not found")

    def search_albums(self, query: str, top_k: int = 3) -> list[Album]:
        documents = self.langchain_qdrant.search(query=query, k=top_k, search_type="similarity", score_threshold=0.7)
        return [_document_to_album(document) for document in documents]

    def search_albums_by_metadata(self, metadata: dict, top_k: int = 3) -> list[Album]:
        raise NotImplementedError

    def update_album(self, album_id: int, updated_album: Album) -> Album | None:
        raise NotImplementedError

    def close(self) -> None:
        self.qdrant_client.close()
        self.langchain_qdrant = None
