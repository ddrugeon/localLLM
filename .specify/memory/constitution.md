# LocalLLM Constitution

<!--
Sync Impact Report (2026-01-14):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: N/A → 1.0.0 (Initial constitution)

New Principles:
  1. Hexagonal Architecture (Ports and Adapters)
  2. Type Safety and Immutability
  3. Test-Driven Development
  4. Code Quality Standards
  5. Async-First Design

New Sections:
  - Technology Constraints
  - Development Workflow

Template Alignment Status:
  ✅ .specify/templates/plan-template.md - Constitution Check section ready
  ✅ .specify/templates/spec-template.md - Requirements align with principles
  ✅ .specify/templates/tasks-template.md - Task categories support testing discipline
  ⚠️  No command-specific templates found in .specify/templates/commands/

Follow-up Items:
  - None - all placeholders filled

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

## Core Principles

### I. Hexagonal Architecture (Ports and Adapters)

The project MUST maintain strict separation of concerns through hexagonal architecture:

- **Domain Layer** contains pure business logic with no infrastructure dependencies
- **Application Layer** orchestrates use cases and depends only on domain abstractions
- **Infrastructure Layer** implements domain ports through adapters (SPI) and provides entry points (API)
- Port interfaces MUST be defined as Python `Protocol` classes in `domain/ports/`
- All external dependencies (databases, APIs, file systems) MUST be abstracted behind ports
- Domain models MUST be technology-agnostic and framework-independent

**Rationale**: Hexagonal architecture ensures testability, maintainability, and flexibility. It allows swapping implementations (e.g., SQLite to PostgreSQL, Qdrant to Pinecone) without modifying business logic. This separation is critical for a project experimenting with different LLM and vector store technologies.

### II. Type Safety and Immutability

Python type hints and immutability MUST be enforced throughout the codebase:

- All functions, methods, and variables MUST have explicit type annotations using Python 3.12+ syntax (`|` for unions)
- Domain models MUST use Pydantic v2 with `frozen=True` for immutability
- No `Any` types unless explicitly justified and documented
- Ruff linter MUST enforce type-related rules in CI/CD pipeline
- Return types MUST be explicit (no implicit `None`)

**Rationale**: Type safety catches errors at development time rather than runtime. Immutable domain models prevent unintended state mutations and make code more predictable, especially critical when dealing with complex album metadata and vector embeddings.

### III. Test-Driven Development

Testing is NON-NEGOTIABLE and follows these mandatory rules:

- All new features MUST have tests written BEFORE implementation when explicitly requested
- Tests MUST use in-memory databases (`sqlite:///:memory:`, `:memory:` for Qdrant) for isolation
- Test structure MUST follow Given-When-Then pattern with descriptive names: `test_action_should_result_when_condition`
- Fixtures MUST be defined in `conftest.py` for reusability
- Async tests MUST use `@pytest.mark.asyncio` decorator
- Service tests MUST use `Mock` and `AsyncMock` for external dependencies
- Test coverage expectations:
  - Domain layer: 100% coverage (pure logic, no excuses)
  - Application layer: >90% coverage (use cases critical)
  - Infrastructure layer: >70% coverage (adapters may have integration test challenges)

**Rationale**: TDD ensures code correctness and prevents regressions. In-memory databases enable fast, isolated tests. The Given-When-Then pattern improves test readability and maintenance. High coverage on domain/application layers protects business logic from bugs.

### IV. Code Quality Standards

Code quality is enforced through automated tools and conventions:

- **Linter/Formatter**: Ruff (configured in `pyproject.toml`)
- **Line length**: 120 characters maximum
- **Python version**: 3.12+ (leveraging modern syntax and performance)
- **Commit messages**: Conventional commits format (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- **Pre-commit hooks**: MUST run and pass before commits
  - YAML validation, trailing whitespace removal, end-of-file fixing
  - Ruff linting and formatting
  - Bandit security checks (excluding tests/)
  - Prettier for JSON/Markdown
- **Code review**: All PRs MUST pass CI/CD checks (test, lint, format)

**Rationale**: Automated quality checks reduce human error and maintain consistency. Ruff provides fast, comprehensive linting and formatting. Conventional commits enable automated changelog generation and semantic versioning via commitizen.

### V. Async-First Design

Asynchronous programming MUST be used for I/O-bound operations:

- External API calls (Discogs, Spotify) MUST be async
- Database operations SHOULD be async where supported by libraries
- Vector store operations (Qdrant) MUST be async
- Use `asyncio.gather()` for concurrent operations (e.g., enriching multiple albums)
- Rate limiting MUST use `tenacity` retry decorators with async support
- Synchronous I/O is permitted only for local file operations where async provides no benefit

**Rationale**: Async operations dramatically improve performance when fetching metadata from multiple external APIs or processing batches of albums. The project's use case (multimedia file management at scale) benefits significantly from concurrent I/O operations.

## Technology Constraints

The following technology stack is MANDATORY and MUST NOT be changed without constitutional amendment:

- **Python**: 3.12.x (specified in `.python-version`)
- **Package Manager**: uv (>=0.4.30) - fast, reliable dependency resolution
- **Task Runner**: go-task (>=3.0.0) - consistent task execution across environments
- **LLM Framework**: Ollama (>=0.4.0) - local LLM execution
- **Vector Store**: Qdrant - high-performance vector similarity search
- **Database**: SQLite via SQLModel/SQLAlchemy - simple, embedded, zero-config
- **Embeddings**: Ollama (snowflake-arctic-embed2) or FastEmbed - local, privacy-preserving
- **External APIs**: Discogs and Spotify - industry-standard metadata sources
- **CLI Framework**: Typer with Rich - modern, type-safe CLI with beautiful output
- **Logging**: structlog - structured, machine-parsable logs

**Technology Change Policy**:
- MINOR version bump: Adding optional alternative (e.g., adding pgvector alongside Qdrant)
- MAJOR version bump: Replacing core technology (e.g., Ollama → LangChain LLM abstraction change)

**Rationale**: These technologies were chosen for local-first operation (privacy), simplicity (SQLite, Ollama), and Python ecosystem maturity. Changes require careful consideration of deployment complexity, privacy implications, and ecosystem lock-in.

## Development Workflow

All development MUST follow this workflow:

1. **Feature Planning**:
   - Use `/speckit.specify` to create feature specification in `specs/[###-feature-name]/spec.md`
   - Use `/speckit.plan` to generate implementation plan with architecture decisions
   - Use `/speckit.tasks` to create dependency-ordered task list in `tasks.md`

2. **Implementation**:
   - Create feature branch: `feat/[feature-name]` or `fix/[issue-name]`
   - Follow hexagonal architecture principles (domain → application → infrastructure)
   - Write tests FIRST when explicitly requested in spec (TDD)
   - Implement in layers: domain models → ports → use cases → adapters → CLI commands
   - Update `factory.py` for dependency injection wiring

3. **Quality Gates** (MUST pass before merge):
   - All tests pass: `task test` or `uv run pytest tests`
   - Linting clean: `task lint` or `uv run ruff check src tests`
   - Formatting applied: `task format` or `uv run ruff format src tests`
   - Pre-commit hooks pass
   - CI/CD pipeline green (GitHub Actions)

4. **Code Review**:
   - PRs MUST reference related spec/plan documents
   - Reviewers MUST verify constitutional compliance
   - Complexity violations MUST be justified in plan.md "Complexity Tracking" section

5. **Commit Standards**:
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
   - Include Co-Authored-By for AI assistance: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
   - Reference issue/spec numbers where applicable

**Workflow Rationale**: Structured planning (speckit) ensures features are well-designed before implementation. Quality gates prevent regressions. Conventional commits enable automated versioning and changelogs. Feature branches isolate work and simplify rollback if needed.

## Governance

This constitution is the authoritative source for project practices and supersedes all conflicting guidance.

**Amendment Process**:
1. Propose amendment via GitHub issue with justification and impact analysis
2. Update constitution.md with sync impact report at top
3. Propagate changes to dependent templates (.specify/templates/*)
4. Update CLAUDE.md if runtime guidance affected
5. Increment version according to semantic versioning:
   - MAJOR: Breaking governance change (e.g., removing mandatory testing)
   - MINOR: New principle added or section expanded
   - PATCH: Clarifications, typo fixes, wording improvements
6. Commit with message: `docs: amend constitution to vX.Y.Z (summary of changes)`

**Compliance Review**:
- All PRs MUST verify compliance with constitutional principles
- Plan templates (`plan-template.md`) MUST include "Constitution Check" section
- Complexity violations MUST be explicitly justified and documented
- Constitutional violations without justification MUST block PR approval

**Version Control**:
- Constitution changes MUST include sync impact report (HTML comment at top)
- Templates MUST be validated for consistency after amendments
- Version number MUST appear in footer: `**Version**: X.Y.Z`

**Rationale**: Explicit governance prevents erosion of core principles over time. Versioning tracks evolution of project standards. Compliance reviews ensure principles are followed in practice, not just documented.

---

**Version**: 1.0.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-14
