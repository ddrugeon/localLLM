from pathlib import Path

import structlog
from localllm.infra.inputs.fetchers import LocalFileJSONReader
from localllm.application.services.service import MultimediaService

from localllm.config import Settings

logger = structlog.getLogger()

def main() -> None:
    settings: Settings = Settings()
    logger.info(f"Settings loaded: {settings}")

    source_file = Path(settings.document_folder, "albums.json")
    fetcher = LocalFileJSONReader()

    service = MultimediaService(fetcher)
    service.load_albums(source_file)