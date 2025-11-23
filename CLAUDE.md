# CLAUDE.md - LocalLLM Project Documentation

## Project Overview

**LocalLLM** is a Python-based multimedia management system that uses local Large Language Models (LLMs) to help users discover and launch multimedia files from a NAS. The project demonstrates integration of LLMs with vector search, metadata enrichment, and structured data management.

### Core Purpose
- Load and enrich album metadata from external sources (Discogs, Spotify)
- Index multimedia content using vector embeddings (via Ollama)
- Provide semantic search capabilities over the multimedia library
- Use local LLMs for natural language queries about the collection

### Key Technologies
- **Python**: 3.12+ (managed with `uv`)
- **LLM Framework**: LangChain + Ollama
- **Vector Database**: Qdrant
- **Embeddings**: Ollama with snowflake-arctic-embed2 model
- **Relational DB**: SQLite (via SQLModel)
- **CLI Framework**: Typer with Rich for UI
- **Testing**: pytest with async support
- **Code Quality**: Ruff (linting + formatting), pre-commit hooks, Bandit (security)

---

## Architecture

This project follows **Hexagonal Architecture** (Ports and Adapters pattern) with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                    (CLI via Typer/Rich)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Application Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         MultimediaIngesterService (Service)             │ │
│  └──┬──────────────────────────────────────────────────┬──┘ │
│     │                                                   │    │
│  ┌──▼────────────────┐                    ┌────────────▼──┐ │
│  │   Use Cases       │                    │  Interfaces   │ │
│  │ - LoadAlbums      │                    │  (Protocols)  │ │
│  │ - EnrichAlbums    │                    └───────────────┘ │
│  │ - StoreAlbums     │                                      │
│  │ - IndexAlbums     │                                      │
│  └───────────────────┘                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Domain Models: Album, Track (Pydantic immutable)      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Ports (Protocols):                                     │ │
│  │  - AlbumEnricher, AlbumFetcher, AlbumPersistence        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ SPI Adapters:   │  │ Persistence: │  │ Web Adapters:  │ │
│  │ - CLI (Typer)   │  │ - SQLite     │  │ - Discogs API  │ │
│  │ - UI (Rich)     │  │ - Qdrant     │  │ - Spotify API  │ │
│  │                 │  │ - JSON Files │  │ - Ollama       │ │
│  └─────────────────┘  └──────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Architectural Principles

1. **Dependency Rule**: Dependencies point inward only (Infrastructure → Application → Domain)
2. **Port & Adapter**: Domain defines interfaces (Protocols), infrastructure implements them
3. **Immutable Domain Models**: `Album` and `Track` are frozen Pydantic models
4. **Protocol-Based Interfaces**: Use Python `Protocol` for dependency inversion
5. **Service Layer**: `MultimediaIngesterService` orchestrates use cases
6. **Separation of Concerns**: Each layer has a single, well-defined responsibility

---

## Directory Structure

```
localLLM/
├── .github/
│   └── workflows/
│       └── main.yaml              # CI/CD pipeline (test, lint, format)
├── data/
│   ├── inputs/                     # Source data files (albums.json)
│   ├── qdrant/                     # Qdrant vector DB storage
│   └── enriched_albums.json        # Output from enrichment process
├── models/
│   └── llama3.modelfile            # Ollama model configuration
├── src/localllm/
│   ├── __init__.py                 # CLI entry point (main function)
│   ├── config.py                   # Settings (Pydantic Settings)
│   ├── factory.py                  # DI/Factory for service creation
│   ├── application/
│   │   ├── services/
│   │   │   └── service.py          # MultimediaIngesterService
│   │   └── use_cases/
│   │       ├── interfaces.py       # Use case protocols
│   │       ├── load_albums.py
│   │       ├── enrich_albums.py
│   │       ├── store_albums.py
│   │       └── index_albums.py
│   ├── domain/
│   │   ├── multimedia.py           # Album, Track models
│   │   └── ports/
│   │       ├── enrichers.py        # AlbumEnricher protocol
│   │       ├── fetchers.py         # AlbumFetcher protocol
│   │       └── persistence.py      # Persistence protocols
│   ├── infra/
│   │   ├── api/cli/                # CLI commands (Typer)
│   │   └── spi/                    # Service Provider Interfaces
│   │       ├── persistence/
│   │       │   ├── file/           # JSON file storage
│   │       │   └── repository/     # SQLite, Qdrant implementations
│   │       ├── ui/cli.py           # CLI feedback
│   │       └── web/
│   │           ├── enrichers.py    # Discogs/Spotify adapters
│   │           └── adapters.py     # HTTP adapters
│   └── presentation/               # (Currently unused)
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_adapters.py
│   ├── test_multimedia_service.py
│   ├── test_qdrant_persistence.py
│   └── test_sqlite_persistence.py
├── .editorconfig                   # Editor configuration
├── .env.example                    # Environment variable template
├── .gitignore
├── .pre-commit-config.yaml         # Pre-commit hooks
├── .python-version                 # Python 3.12
├── compose.yml                     # Docker Compose (Qdrant service)
├── Dockerfile
├── pyproject.toml                  # Project metadata, dependencies
├── README.md
├── Taskfile.yml                    # Task runner definitions
└── uv.lock                         # Dependency lock file
```

### Layer Responsibilities

- **`domain/`**: Pure business logic, domain models, port definitions (no external dependencies)
- **`application/`**: Use cases orchestrating domain logic, service layer
- **`infra/`**: All external integrations (APIs, databases, file systems, CLI)
- **`presentation/`**: Future UI layer (currently CLI is in `infra/api/cli`)

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd localLLM

# Install dependencies
uv install

# Set up pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# - DISCOGS_USER_TOKEN
# - SPOTIFY_CLIENT_ID
# - SPOTIFY_CLIENT_SECRET
# - DATABASE_MODEL_URL
# - VECTOR_MODEL_URL
```

### Common Tasks (via go-task)

```bash
task                    # List all available tasks
task format             # Format code with Ruff
task lint               # Lint code with Ruff
task test               # Run pytest
task run                # Run the CLI application
task start-qdrant       # Start Qdrant via Docker Compose
task stop-qdrant        # Stop Qdrant
task start-ollama       # Start Ollama server
```

### CLI Commands

```bash
# Ingest albums from JSON
uv run localllm ingest --file data/inputs/albums.json

# Ingest and enrich with external APIs
uv run localllm ingest --enrich --store

# Index albums into vector database
uv run localllm index --file data/enriched_albums.json

# Search albums semantically
uv run localllm search "jazz albums from the 60s" --top-k 5

# Query with LLM
uv run localllm serve "play some relaxing music"
```

### Git Workflow

```bash
# Branches follow pattern: feature/*, fix/*, feat/*
git checkout -b feature/my-new-feature

# Make changes, then run pre-commit checks
git add .
pre-commit run --all-files

# Commit using conventional commits
git commit -m "feat(search): add fuzzy matching for album titles"

# Push and create PR
git push -u origin feature/my-new-feature
```

---

## Code Conventions

### General Python Style

- **Line length**: 120 characters (configured in Ruff)
- **Python version**: 3.12+
- **Type hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings for public APIs
- **Imports**: Organized by Ruff (stdlib → third-party → local)

### Naming Conventions

- **Classes**: PascalCase (`MultimediaIngesterService`, `Album`)
- **Functions/Variables**: snake_case (`load_albums`, `album_id`)
- **Constants**: UPPER_SNAKE_CASE (`PROMPT_TEMPLATE`, `ROOT_DIR`)
- **Private members**: Prefix with `_` (`_load_albums_use_case`)
- **Protocols**: Descriptive names ending in protocol role (`AlbumEnricher`, `LoadAlbumUseCase`)

### Domain Model Conventions

```python
# Domain models are immutable Pydantic models
class Album(BaseModel):
    class Config:
        frozen = True  # Immutable

    # Required fields with validation
    album_id: str = Field(..., description="Unique identifier")
    title: str = Field(..., min_length=1)

    # Optional fields with defaults
    genres: list[str] = Field(default_factory=list)
```

### Protocol Usage (Ports)

```python
from typing import Protocol

class AlbumEnricher(Protocol):
    """Port definition for album enrichment."""

    async def get_album_metadata(self, artist: str, album: str) -> Album | None:
        """Contract for enrichment implementations."""
        ...
```

### Dependency Injection Pattern

All dependencies are injected via `factory.py`:

```python
def create_multimedia_service() -> MultimediaIngesterService:
    settings = Settings()  # Load from .env

    # Create adapters
    fetcher = LocalFileJSONReader()
    enrichers = [DiscogsAlbumEnricher(...), SpotifyAlbumEnricher(...)]

    # Inject into service
    return MultimediaIngesterService(
        load_albums_use_case=LoadAlbums(fetcher),
        enrich_album_use_case=EnrichAlbums(enrichers),
        # ... more use cases
    )
```

### Async/Await Usage

- External API calls are `async` (Discogs, Spotify enrichers)
- Use `asyncio.run()` in CLI for async operations
- Database operations can be sync or async depending on driver

### Error Handling

- Use standard Python exceptions
- Log errors with `structlog`
- Return `None` from protocols when data not found (e.g., `get_album_metadata`)

### Logging

```python
import structlog

logger = structlog.getLogger(__name__)

# Usage
logger.info("Loading albums", file_path=path)
logger.debug("Settings loaded", settings=settings.model_dump())
logger.error("Failed to enrich album", artist=artist, album=album, exc_info=True)
```

---

## Testing Strategy

### Test Organization

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test adapter implementations (SQLite, Qdrant)
- **Service tests**: Test service orchestration
- **Fixtures**: Centralized in `conftest.py`

### Running Tests

```bash
# Run all tests
task test
# or
uv run pytest

# Run with coverage
uv run pytest --cov=src/localllm --cov-report=html

# Run specific test file
uv run pytest tests/test_multimedia_service.py

# Run tests matching pattern
uv run pytest -k "test_enrich"
```

### Test Conventions

```python
# Use descriptive test names
def test_load_albums_returns_list_of_albums():
    ...

# Use fixtures for common setup
@pytest.fixture
def sample_albums():
    return [
        Album(album_id="1", title="Test Album", artist="Test Artist", year=2020)
    ]

# Test async code
@pytest.mark.asyncio
async def test_enrich_albums_with_external_api():
    ...
```

### Mocking External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_discogs_enricher():
    with patch('discogs_client.Client') as mock_client:
        mock_client.return_value.search.return_value = [...]
        enricher = DiscogsAlbumEnricher(token="fake")
        result = await enricher.get_album_metadata("Artist", "Album")
```

---

## Key Patterns to Follow

### 1. Adding a New Use Case

1. Define protocol in `application/use_cases/interfaces.py`
2. Implement use case in `application/use_cases/new_use_case.py`
3. Update `MultimediaIngesterService` to inject and use it
4. Add adapter implementation in `infra/spi/`
5. Update `factory.py` to wire dependencies
6. Add CLI command in `infra/api/cli/__init__.py`

### 2. Adding a New External Service

1. Define port (Protocol) in `domain/ports/`
2. Implement adapter in `infra/spi/web/` or `infra/spi/persistence/`
3. Add configuration to `config.py` (API keys, URLs)
4. Update `.env.example` with new variables
5. Wire in `factory.py`
6. Add tests with mocked responses

### 3. Adding a New Domain Model

1. Create immutable Pydantic model in `domain/multimedia.py`
2. Use `Field()` with descriptions and validation
3. Set `Config.frozen = True` for immutability
4. Add `__str__` for human-readable representation
5. Update related ports/use cases

### 4. Modifying the Service

- Always inject dependencies, never instantiate in service
- Keep service methods thin (delegate to use cases)
- Use async methods when orchestrating async use cases
- Log at service boundaries

---

## Environment Configuration

### Required Environment Variables

```bash
# External API credentials
DISCOGS_USER_TOKEN="your_discogs_token"
SPOTIFY_CLIENT_ID="your_spotify_client_id"
SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"

# Database URLs
DATABASE_MODEL_URL="sqlite:///database/db"      # SQLite file path
VECTOR_MODEL_URL="http://localhost:6333"        # Qdrant URL (or :memory:)
```

### Ollama Setup

```bash
# Start Ollama server
task start-ollama

# Pull required models
ollama pull llama3
ollama pull snowflake-arctic-embed2

# Create custom intent detection model (optional)
ollama create intent -f models/llama3.modelfile
```

### Qdrant Setup

```bash
# Start Qdrant via Docker
task start-qdrant

# Qdrant will be available at:
# - HTTP: http://localhost:6333
# - gRPC: localhost:6334
# - Dashboard: http://localhost:6333/dashboard
```

---

## Code Quality Tools

### Pre-commit Hooks

Automatically run on `git commit`:

1. **check-yaml**: Validate YAML files
2. **end-of-file-fixer**: Ensure files end with newline
3. **trailing-whitespace**: Remove trailing whitespace
4. **ruff**: Lint Python code
5. **bandit**: Security vulnerability scanning (excludes tests/)
6. **prettier**: Format Markdown, JSON, YAML

### Ruff Configuration

Configured in `pyproject.toml`:

- **Enabled rules**: Extensive (E, F, W, UP, I, D200-D419, PERF, etc.)
- **Line length**: 120
- **Target**: Python 3.12
- **Special**: Tests can use assert (`S101` ignored)

### CI/CD Pipeline

GitHub Actions (`.github/workflows/main.yaml`):

1. Install Python 3.12 + uv
2. Install dependencies (`uv sync --all-extras`)
3. Run tests (`pytest`)
4. Run linter (`ruff check`)
5. Check formatting (`ruff format --check`)

---

## Common Gotchas

### 1. Async Context

Many operations are async (enrichment, some persistence). Always use:

```python
# In CLI
asyncio.run(application.enrich_albums(albums))

# In tests
@pytest.mark.asyncio
async def test_something():
    ...
```

### 2. Immutable Domain Models

Albums are frozen. To modify, create a new instance:

```python
# Wrong
album.title = "New Title"  # Raises error

# Correct
updated_album = album.model_copy(update={"title": "New Title"})
```

### 3. Environment Variables

Always use `Settings()` from `config.py`:

```python
from localllm.config import Settings

settings = Settings()  # Loads from .env
token = settings.discogs_user_token.get_secret_value()
```

### 4. Vector Embeddings

The embedding model determines vector size. Don't hardcode:

```python
# Correct (in factory.py)
embeddings = OllamaEmbeddings(model="snowflake-arctic-embed2")
vector_size = len(embeddings.embed_query("test"))
```

### 5. Qdrant Collection Creation

Collections are created automatically on first index. Ensure Qdrant is running:

```bash
task start-qdrant
# Wait for startup
uv run localllm index
```

---

## AI Assistant Guidelines

### When Modifying Code

1. **Respect architecture**: Never violate dependency rules (no domain → infra imports)
2. **Use protocols**: Define ports before implementations
3. **Inject dependencies**: Update `factory.py` for new dependencies
4. **Maintain immutability**: Domain models must stay frozen
5. **Add tests**: Every new feature needs corresponding tests
6. **Update documentation**: Keep this file current with changes

### When Adding Features

1. Start with domain model/port definition
2. Implement use case in application layer
3. Create adapter in infrastructure layer
4. Wire in factory
5. Add CLI command
6. Write tests (unit + integration)
7. Update `.env.example` if adding config

### When Debugging

1. Check logs (structlog output)
2. Verify environment variables in `.env`
3. Ensure external services are running (Ollama, Qdrant)
4. Run tests to isolate issues: `task test`
5. Use `task lint` to catch code issues

### Code Review Checklist

- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] Tests added/updated
- [ ] Pre-commit hooks pass
- [ ] No domain → infrastructure imports
- [ ] Dependencies injected via factory
- [ ] Async/await used correctly
- [ ] Logging added at key points
- [ ] Environment variables in `.env.example`
- [ ] Conventional commit message

---

## Resources

- **LangChain Docs**: https://python.langchain.com/
- **Ollama**: https://ollama.ai/
- **Qdrant**: https://qdrant.tech/documentation/
- **Pydantic**: https://docs.pydantic.dev/
- **Typer**: https://typer.tiangolo.com/
- **Ruff**: https://docs.astral.sh/ruff/
- **Hexagonal Architecture**: https://alistair.cockburn.us/hexagonal-architecture/

---

## Version History

- **Current**: v0.1.0
- **Last Updated**: 2025-11-23
- **Architecture**: Hexagonal (Ports & Adapters)
- **Python**: 3.12+
- **Package Manager**: uv

---

## Maintenance Notes

This document should be updated when:

- New layers/modules are added
- Architecture patterns change
- External dependencies are added/removed
- Development workflow changes
- New environment variables are introduced
- Testing strategy evolves

Keep this file as the single source of truth for AI assistants working on this codebase.
