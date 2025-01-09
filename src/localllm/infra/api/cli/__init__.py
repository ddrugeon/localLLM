import asyncio
from pathlib import Path

import structlog
import typer
from rich.console import Console
from rich.table import Table

from localllm.factory import create_multimedia_service

logger = structlog.get_logger(__name__)
app = typer.Typer(help="CLI to manage multimedia content in the localllm project.")
console = Console()

@app.command()
def ingest(enrich: bool = False, file: Path = Path("data/inputs/albums.json"), store: bool = False):
    """
    Ingest albums.

    This command ingests albums from a source file and stores them into local sqlite database.
    Optionally, it can enrich the albums with additional metadata from external services.
    """
    application = create_multimedia_service()
    albums = application.load_albums(album_file_path=file)
    if enrich:
        albums = asyncio.run(application.enrich_albums(albums=albums))
        application.save_albums(albums=albums, path=Path("data/enriched_albums.json"))

    if store:
        asyncio.run(application.store_albums(albums=albums))

@app.command()
def index(file: Path = Path("data/inputs/albums.json")):
    """Index albums into vector store."""
    application = create_multimedia_service()
    albums = application.load_albums(album_file_path=file)
    application.index_albums(albums=albums)

@app.command()
def search(query: str, top_k: int = 5):
    """Search albums."""
    application = create_multimedia_service()
    albums = application.search_albums(query=query, top_k=top_k)

    table = Table("Name", "Artist", "Year")
    for album in albums:
        table.add_row(album.title, album.artist, str(album.year))

    console.print(table)
