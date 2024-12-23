import json
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TrackEntity(SQLModel, table=True):
    __tablename__ = "track"

    id: int | None = Field(default=None, primary_key=True)
    position: str
    title: str = Field(index=True)
    duration: str
    album_id: int | None = Field(default=None, foreign_key="album.id")
    album: Optional["AlbumEntity"] = Relationship(back_populates="tracklist")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AlbumEntity(SQLModel, table=True):
    __tablename__ = "album"

    id: int | None = Field(default=None, primary_key=True)
    album_id: str = Field(index=True, unique=True)
    title: str = Field(index=True, unique=False)
    artist: str = Field(index=True, unique=False)
    year: int
    genres: str = Field(default="[]", index=True, unique=False)
    styles: str = Field(default="[]")
    labels: str = Field(default="[]")
    country: str | None = None
    tracklist: list[TrackEntity] = Relationship(
        back_populates="album", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    credits: str | None = None
    external_urls: str = Field(default="{}")
    external_ids: str = Field(default="{}")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **data):
        if "genres" in data and isinstance(data["genres"], list):
            data["genres"] = json.dumps(data["genres"])
        if "styles" in data and isinstance(data["styles"], list):
            data["styles"] = json.dumps(data["styles"])
        if "labels" in data and isinstance(data["labels"], list):
            data["labels"] = json.dumps(data["labels"])
        if "external_urls" in data and isinstance(data["external_urls"], dict):
            data["external_urls"] = json.dumps(self._convert_urls_to_str(data["external_urls"]))
        if "external_ids" in data and isinstance(data["external_ids"], dict):
            data["external_ids"] = json.dumps(data["external_ids"])
        super().__init__(**data)

    def _convert_urls_to_str(self, urls: dict) -> dict:
        return {key: str(value) for key, value in urls.items()}

    # Getters et setters pour les listes/dicts
    @property
    def genres_list(self) -> list[str]:
        return json.loads(self.genres)

    @genres_list.setter
    def genres_list(self, value: list[str]):
        self.genres = json.dumps(value)

    @property
    def styles_list(self) -> list[str]:
        return json.loads(self.styles)

    @styles_list.setter
    def styles_list(self, value: list[str]):
        self.styles = json.dumps(value)

    @property
    def labels_list(self) -> list[str]:
        return json.loads(self.labels)

    @labels_list.setter
    def labels_list(self, value: list[str]):
        self.labels = json.dumps(value)

    @property
    def external_urls_dict(self) -> dict:
        return json.loads(self.external_urls)

    @external_urls_dict.setter
    def external_urls_dict(self, value: dict):
        self.external_urls = json.dumps(self._convert_urls_to_str(value))

    @property
    def external_ids_dict(self) -> dict:
        return json.loads(self.external_ids)

    @external_ids_dict.setter
    def external_ids_dict(self, value: dict):
        self.external_ids = json.dumps(value)
