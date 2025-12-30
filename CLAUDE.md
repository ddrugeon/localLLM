# CLAUDE.md - AI Assistant Guide for LocalLLM

## Project Overview

LocalLLM is a Python project for experimenting with SLM/LLM to help manage and search multimedia files (specifically music albums) stored on a NAS using a local LLM. The project uses a hexagonal architecture (ports and adapters) pattern.

## Technology Stack

- **Python**: 3.12.x (specified in `.python-version`)
- **Package Manager**: uv (>=0.4.30)
- **Task Runner**: go-task (>=3.0.0)
- **LLM**: Ollama (>=0.4.0)
- **Vector Store**: Qdrant
- **Database**: SQLite (via SQLModel/SQLAlchemy)
- **Embeddings**: Ollama (snowflake-arctic-embed2 model) or FastEmbed
- **External APIs**: Discogs, Spotify (for album metadata enrichment)

## Quick Reference Commands

```bash
# Install dependencies
uv sync --all-extras --group dev --group test

# Run tests
task test
# or directly:
uv run pytest tests

# Lint code
task lint
# or:
uv run ruff check src tests

# Format code
task format
# or:
uv run ruff format src tests

# Run the CLI application
task run
# or:
uv run localllm

# Start Qdrant (vector database)
task start-qdrant  # uses docker compose

# Stop Qdrant
task stop-qdrant

# Start Ollama
task start-ollama  # runs: ollama serve --host 0.0.0.0
```

## Project Structure

```
localLLM/
├── src/localllm/
│   ├── __init__.py          # Entry point (main function)
│   ├── config.py             # Settings via pydantic-settings
│   ├── factory.py            # Service factory (DI composition root)
│   ├── domain/               # Domain layer (business logic)
│   │   ├── multimedia.py     # Album and Track domain models
│   │   └── ports/            # Port interfaces (abstractions)
│   │       ├── enrichers.py  # AlbumEnricher protocol
│   │       ├── fetchers.py   # AlbumFileReader protocol
│   │       └── persistence.py # AlbumRepository, AlbumVectorRepository protocols
│   ├── application/          # Application layer
│   │   ├── services/         # Application services
│   │   │   └── service.py    # MultimediaIngesterService (orchestrator)
│   │   └── use_cases/        # Use case implementations
│   │       ├── interfaces.py # Use case protocols
│   │       ├── load_albums.py
│   │       ├── enrich_albums.py
│   │       ├── store_albums.py
│   │       └── index_albums.py
│   ├── infra/                # Infrastructure layer
│   │   ├── api/              # Driving adapters (entry points)
│   │   │   └── cli/          # Typer CLI application
│   │   └── spi/              # Driven adapters (implementations)
│   │       ├── persistence/
│   │       │   ├── file/     # JSON file reader/writer
│   │       │   └── repository/
│   │       │       ├── databases.py  # SQLite persistence
│   │       │       ├── vectors.py    # Qdrant vector store
│   │       │       └── models.py     # SQLModel entities
│   │       ├── ui/           # CLI utilities
│   │       └── web/          # External API enrichers
│   │           ├── adapters.py    # Discogs/Spotify adapters
│   │           └── enrichers.py   # API enricher implementations
│   └── presentation/         # (Reserved for future use)
├── tests/                    # Test suite
│   ├── conftest.py           # Shared fixtures
│   ├── test_multimedia_service.py
│   ├── test_sqlite_persistence.py
│   ├── test_qdrant_persistence.py
│   └── test_adapters.py
├── data/
│   └── inputs/               # Input JSON files (albums.json)
├── models/                   # Ollama model files
└── Taskfile.yml              # Task definitions
```

## Architecture

### Hexagonal Architecture (Ports and Adapters)

The project follows hexagonal architecture:

1. **Domain Layer** (`domain/`): Core business logic
   - `Album` and `Track` Pydantic models (immutable, frozen=True)
   - Port interfaces defined as Python `Protocol` classes

2. **Application Layer** (`application/`):
   - Use cases implement business operations
   - `MultimediaIngesterService` orchestrates use cases
   - Depends only on domain layer

3. **Infrastructure Layer** (`infra/`):
   - **API (Driving)**: CLI commands that trigger application logic
   - **SPI (Driven)**: Implementations of domain ports
     - Database persistence (SQLite via SQLModel)
     - Vector store (Qdrant via langchain-qdrant)
     - File I/O (JSON)
     - External APIs (Discogs, Spotify)

### Key Domain Models

```python
# Album - Core domain entity
class Album(BaseModel):
    album_id: str           # Required
    title: str              # Required
    artist: str             # Required
    year: int               # Required (0 <= year <= current year)
    genres: list[str]       # Optional
    styles: list[str]       # Optional
    labels: list[str]       # Optional
    country: str | None     # Optional
    tracklist: list[Track]  # Optional
    credits: str | None     # Optional
    popularity: int | None  # Optional (0-100)
    external_urls: dict[str, HttpUrl]
    external_ids: dict[str, str]

# Track - Nested domain entity
class Track(BaseModel):
    position: int
    title: str
    duration: int | None
```

## CLI Commands

The application exposes these CLI commands:

```bash
# Ingest albums from JSON file
localllm ingest [--enrich] [--file PATH] [--store]

# Index albums into vector store
localllm index [--file PATH]

# Search albums using natural language
localllm search "query" [--top-k 5]

# Search with LLM-powered response
localllm serve "query" [--top-k 5]
```

## Configuration

Environment variables (see `.env.example`):

```bash
DISCOGS_USER_TOKEN="your_token"
SPOTIFY_CLIENT_ID="your_client_id"
SPOTIFY_CLIENT_SECRET="your_client_secret"
DATABASE_MODEL_URL="sqlite:///database/db"
VECTOR_MODEL_URL=":memory:"  # or Qdrant URL
```

## Development Guidelines

### Code Style

- **Linter/Formatter**: Ruff (configured in `pyproject.toml`)
- **Line length**: 120 characters
- **Target Python**: 3.12
- **Style rules**: PEP 8 + additional rules (see `tool.ruff.lint.extend-select`)

### Pre-commit Hooks

The project uses pre-commit with:
- `pre-commit-hooks`: YAML check, trailing whitespace, end-of-file fixer
- `ruff`: Linting
- `bandit`: Security checks (excludes tests/)
- `prettier`: JSON/Markdown formatting

### Testing Conventions

- **Framework**: pytest with pytest-asyncio
- **Test location**: `tests/` directory
- **Fixtures**: Defined in `conftest.py`
- **Patterns**:
  - Use `@pytest.fixture` for test data
  - Use `@pytest.mark.asyncio` for async tests
  - Use in-memory databases (`sqlite:///:memory:`, `:memory:` for Qdrant)
  - Use `Mock` and `AsyncMock` for service tests
  - Follow Given-When-Then pattern in test names

Example test structure:
```python
def test_action_should_result_when_condition(repository, fixture):
    # Given (setup in fixtures)
    # When
    result = repository.some_action()
    # Then
    assert result == expected
```

### Adding New Features

1. **New Domain Entity**: Add to `domain/multimedia.py`
2. **New Port**: Add protocol to `domain/ports/`
3. **New Use Case**: Add to `application/use_cases/` with interface in `interfaces.py`
4. **New Adapter**: Add implementation to appropriate `infra/spi/` subdirectory
5. **Wire Dependencies**: Update `factory.py` for DI

### Commit Message Convention

Uses conventional commits (commitizen configured):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance

## CI/CD

GitHub Actions workflow (`.github/workflows/main.yaml`):
- Triggers on push/PR to `main`
- Steps: Install deps -> Test -> Lint -> Format check

## Dependencies Overview

### Production
- `langchain`, `langchain-ollama`, `langchain-qdrant`, `langchain-community`
- `pydantic`, `pydantic-settings`
- `sqlmodel` (SQLAlchemy + Pydantic)
- `typer`, `rich` (CLI)
- `structlog` (Logging)
- `spotipy`, `python3-discogs-client` (API clients)
- `fastembed`, `sentence-transformers` (Embeddings)
- `tenacity` (Retry logic)

### Development
- `ruff`, `ruff-lsp`
- `pre-commit`
- `coverage`

### Testing
- `pytest`, `pytest-asyncio`, `pytest-cov`
- `anyio`

## Common Tasks for AI Assistants

1. **Adding a new enricher**: Implement `AlbumEnricher` protocol in `infra/spi/web/enrichers.py`
2. **Adding a new storage backend**: Implement `AlbumRepository` or `AlbumVectorRepository` protocol
3. **Adding CLI command**: Add function with `@app.command()` decorator in `infra/api/cli/__init__.py`
4. **Modifying album fields**: Update `Album` model in `domain/multimedia.py` and corresponding entity in `infra/spi/persistence/repository/models.py`

## Important Notes

- The project uses Python type hints extensively with `|` union syntax (Python 3.10+)
- Domain models use Pydantic v2 (`model_dump()`, `model_validate()`)
- Async operations use `asyncio.gather()` for concurrent execution
- Rate limiting is handled with `tenacity` retry decorators
- Album models are immutable (`frozen=True` in Pydantic config)
