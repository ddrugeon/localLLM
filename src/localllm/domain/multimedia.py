from datetime import date

import structlog
from pydantic import BaseModel, Field, HttpUrl

logger = structlog.getLogger()


class Track(BaseModel):
    """
    Track is a class that represents a music track in the multimedia library.

    Attributes:
    - position: int, the position of the track in the album
    - title: str, the title of the track
    - duration: int, the duration of the track in seconds (optional).
    """

    position: int = Field(..., description="The position of the track in the album")
    title: str = Field(..., description="The title of the track")
    duration: int | None = Field(None, description="The duration of the track in seconds")


class Album(BaseModel):
    """
    Album is a class that represents an album in the multimedia library.

    Attributes:
    - album_id: str, Album ID in our local library
    - title: str, Album title
    - artist: str, Main artist name
    - year: int, release year

    Optional attributes:
    - genres: genre list
    - styles: style of music (subgenres)
    - labels: label list
    - country: country of release
    - tracklist: track list
    - credits: additional artists credits
    - popularity: popularity score
    - external_urls: external service URLs
    - external_ids: external service IDs
    """

    # Required fields
    album_id: str = Field(..., description="Unique identifier for the album")
    title: str = Field(..., description="Album title", min_length=1)
    artist: str = Field(..., description="Main artist name")
    year: int = Field(..., ge=0, le=date.today().year)

    # Optional fields
    genres: list[str] = Field(default_factory=list, description="Music genres")
    styles: list[str] = Field(
        default_factory=list, description="Music styles (subgenres)"
    )
    labels: list[str] = Field(default_factory=list, description="Record labels")
    country: str | None = Field(None, description="Country of release")
    tracklist: list[Track] = Field(default_factory=list, description="list of tracks")
    credits: str | None = Field(None, description="Additional artists credits")
    popularity: int | None = Field(
        None, ge=0, le=100, description="Popularity score (0-100)"
    )
    external_urls: dict[str, HttpUrl] = Field(
        default_factory=dict, description="External service URLs"
    )
    external_ids: dict[str, str] = Field(
        default_factory=dict, description="External service IDs"
    )

    class Config:
        frozen = True

    def __str__(self) -> str:
        base = f"{self.title} by {self.artist} ({self.year})"
        if self.genres:
            base += f" | Genres: {', '.join(self.genres)}"
        if self.labels:
            base += f" | Labels: {', '.join(self.labels)}"
        return base
