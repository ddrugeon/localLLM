from pathlib import Path

import json
import structlog

from localllm.domain.multimedia import Album
from localllm.domain.ports.fetchers import AlbumFileReader

logger = structlog.getLogger()


def json_to_album(json_album: dict) -> Album:
    return Album(
        album_id=json_album["id"],
        title=json_album["album"],
        artist=json_album["artist"],
        year=json_album["year"],
    )


class LocalFileJSONReader(AlbumFileReader):
    def read(self, path: Path) -> list[Album]:
        """Reads albums from a JSON file."""

        logger.debug(f"Reading albums from {path}")

        with open(path, "r") as json_document:
            data = json.load(json_document)

            json_albums = data["result"]["albums_loop"]

            return [json_to_album(json_album) for json_album in json_albums]
