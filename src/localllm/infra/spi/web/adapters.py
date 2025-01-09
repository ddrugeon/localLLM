import re
from abc import ABC, abstractmethod

import structlog

from localllm.domain.multimedia import Album, Track

logger = structlog.getLogger()


class AlbumAdapter(ABC):
    """
    Interface abstraite pour les adaptateurs de métadonnées d'albums.
    """  # noqa: D200

    @abstractmethod
    def to_album(self, metadata: dict) -> Album | None:
        """
        Convertit les métadonnées en objet Album.

        Args:
            metadata: Dictionnaire contenant les métadonnées de l'album

        Returns:
            Optional[Album]: L'objet Album converti ou None si les métadonnées sont invalides
        """
        pass

    def _create_tracks(self, track_data: list[dict]) -> set[Track]:
        """
        Crée une liste de pistes à partir des données brutes.

        Args:
            track_data: Liste des données brutes des pistes

        Returns:
            List[Track]: Liste des objets Track
        """
        return {
            Track(
                position=str(track.get("position", "")),
                title=track.get("title", ""),
                duration=str(track.get("duration", "")),
            )
            for track in track_data
            }



class DiscogsAlbumAdapter(AlbumAdapter):
    """
    Adaptateur pour convertir les métadonnées Discogs en objets Album.
    """  # noqa: D200

    def _parse_title(self, title: str) -> tuple[str | None, str]:
        """
        Extrait l'artiste et le titre de la chaîne de titre Discogs.

        Args:
            title: Titre au format "Artiste - Titre"

        Returns:
            tuple[str | None, str]: (artiste, titre)
        """
        if " - " in title:
            artist, album = title.split(" - ", 1)
            return artist, album
        return None, title

    def to_album(self, metadata: dict) -> Album | None:
        if not metadata:
            return None

        logger.debug("Converting Discogs metadata to Album object", metadata=metadata)
        try:
            title = metadata.get("title", None)
            artist, album_title = self._parse_title(title) if title is not None else (None, None)

            external_urls = {}
            if discogs_url := metadata.get("resource_url"):
                external_urls["discogs"] = discogs_url

            return Album(
                album_id=f"discogs_{metadata.get('id')}",
                title=album_title,
                artist=artist,
                year=int(metadata.get("year", 0)),
                genres=metadata.get("genre", set()),
                styles=metadata.get("style", set()),
                labels=metadata.get("label", set()),
                country=metadata.get("country"),
                tracklist=self._create_tracks(metadata.get("tracklist", [])),
                credits=metadata.get("credits"),
                external_urls=external_urls,
                external_ids={"discogs": str(metadata.get("id"))},
            )
        except (KeyError, ValueError) as e:
            logger.error("Erreur lors de la conversion des métadonnées Discogs", error=str(e))
            return None


class SpotifyAlbumAdapter(AlbumAdapter):
    """
    Adaptateur pour convertir les métadonnées Spotify en objets Album.
    """  # noqa: D200

    def _extract_spotify_id(self, url: str) -> str | None:
        """
        Extrait l'ID Spotify de l'URL de l'album.

        Args:
            url: URL de l'album Spotify

        Returns:
            Optional[str]: ID Spotify ou None si non trouvé
        """
        if match := re.search(r"album/([a-zA-Z0-9]+)", url):
            return match.group(1)
        return None

    def _parse_year(self, release_date: str) -> int:
        """
        Extrait l'année de la date de sortie.

        Args:
            release_date: Date de sortie au format "YYYY" ou "YYYY-MM-DD"

        Returns:
            int: Année extraite ou 0 si invalide
        """
        try:
            year_str = release_date.split("-")[0]
            return int(year_str) if year_str.isdigit() else 0
        except (ValueError, AttributeError):
            return 0

    def to_album(self, metadata: dict) -> Album | None:
        if not metadata:
            return None

        try:
            external_urls = metadata.get("external_urls", {})
            if spotify_url := metadata.get("spotify_url"):
                external_urls["spotify"] = spotify_url

            release_id = metadata.get("id", "")
            artists = metadata.get("artists", [])
            return Album(
                album_id=f"spotify_{release_id}",
                title=metadata.get("name", "Unknown"),
                artist=artists[0].get("name", "Unknown") if artists else "Unknown",
                year=self._parse_year(metadata.get("release_date", "0")),
                genres=metadata.get("genres", set()),
                labels=[metadata.get("label")] if metadata.get("label") else set(),
                tracklist=self._create_tracks(metadata.get("tracks", [])),
                popularity=metadata.get("popularity"),
                external_urls=external_urls,
                external_ids={"spotify": release_id},
            )
        except (KeyError, ValueError) as e:
            logger.error("Error when getting metadata from Spotify", error=str(e))
            return None
