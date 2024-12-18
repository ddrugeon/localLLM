import json
from pathlib import Path

import structlog

from localllm.domain.multimedia import Album
from localllm.domain.ports.fetchers import AlbumFileReader

logger = structlog.getLogger()


def json_to_album(json_album: dict) -> Album:
    """
    Converts a JSON album to an Album object.

    :param json_album: dict, the JSON album
    :return: Album, the Album object
    """
    logger.debug(f"Converting JSON album {json_album}")

    return Album(
        album_id=str(json_album["id"]),
        title=json_album["album"],
        artist=json_album["artist"],
        year=json_album["year"],
    )


class LocalFileJSONReader(AlbumFileReader):
    def read(self, path: Path) -> list[Album]:
        """
        Reads albums from a JSON file.

        :param path: Path, the path to the JSON file
        :return: list[Album], the albums read from the JSON file
        """

        logger.debug(f"Reading albums from {path}")

        try:
            with open(path) as json_document:
                data = json.load(json_document)

                json_albums = data["result"]["albums_loop"]

                return [json_to_album(json_album) for json_album in json_albums]
        except FileNotFoundError as e:
            logger.error(f"File not found: {path}")
            raise e
