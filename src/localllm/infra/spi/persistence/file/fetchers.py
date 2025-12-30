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

    if "id" in json_album:
        album_id = str(json_album["id"])
    elif "album_id" in json_album:
        album_id = json_album["album_id"]
    else:
        album_id = ""

    if "album" in json_album:
        title = json_album["album"]
    elif "title" in json_album:
        title = json_album["title"]
    else:
        title = ""
    return Album(
        album_id=album_id,
        title=title,
        artist=json_album["artist"],
        year=json_album["year"],
        genres=json_album["genres"] if "genres" in json_album else [],
        styles=json_album["styles"] if "styles" in json_album else [],
        labels=json_album["labels"] if "labels" in json_album else [],
        country=json_album["country"] if "country" in json_album else "",
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

                if "result" not in data:
                    if isinstance(data, list):
                        json_albums = data
                else:
                    json_albums = data["result"]["albums_loop"]

                return [json_to_album(json_album) for json_album in json_albums]
        except FileNotFoundError as e:
            logger.error(f"File not found: {path}")
            raise e
