import json
from pathlib import Path

from localllm.domain.multimedia import Album
from localllm.domain.ports.persistence import AlbumFileStorage


class JSONAlbumFileStorage(AlbumFileStorage):
    """
    JSON Album Persistence class.

    This class is responsible for storing albums to a JSON file.
    """

    def save(self, path: Path, albums: list[Album]) -> None:
        """
        Saves albums to a JSON file.

        :param path: Path, the path to the file
        :param albums: list[Album], the albums to be saved
        :return: None
        """
        with open(path, "w") as json_file:
            json.dump([album.model_dump(mode="json") for album in albums], json_file, indent=4)
