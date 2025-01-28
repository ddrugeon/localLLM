import asyncio
from pathlib import Path

import structlog
import typer
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from rich.console import Console
from rich.table import Table

from localllm.factory import create_multimedia_service

logger = structlog.get_logger(__name__)
app = typer.Typer(help="CLI to manage multimedia content in the localllm project.")
console = Console()

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


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

    table = Table("Name", "Artist", "Year", "Score")
    for album in albums:
        table.add_row(album[0].title, album[0].artist, str(album[0].year), str(album[1]))

    console.print(table)

@app.command()
def serve(query: str, top_k: int = 5):
    application = create_multimedia_service()
    results = application.search_albums(query=query, top_k=top_k)

    table = Table("Name", "Artist", "Year", "Score")
    for album in results:
        table.add_row(album[0].title, album[0].artist, str(album[0].year), str(album[1]))

    console.print(table)

    context = "\n\n---\n\n".join([
        f"{score} - {album.album_id} - {album.title} by {album.artist} "
        f"- {album.year} - {album.genres}" for album, score in results
    ])
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt_formatted_str: str = prompt.format(question=query, context=context)

    llm = OllamaLLM(
    model="intent",
    temperature=0,
    # other params...
    )

    logger.info("Invoking LLM...")
    response = llm.invoke(prompt_formatted_str)
    console.print(response)
