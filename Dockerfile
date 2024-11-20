FROM python:3.12.0-slim-bookworm AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WORKDIR_PATH="/opt/localLLM" \
    VIRTUAL_ENV="/opt/localLLM/.venv"

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM python-base AS builder-base

COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /bin/uv

WORKDIR $WORKDIR_PATH

COPY . .

RUN uv sync --frozen

FROM builder-base AS development

CMD ["python","-m", "localllm.main"]

FROM python-base AS production

COPY --from=builder-base $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR $WORKDIR_PATH

COPY ./src/ ./

USER 10000

CMD ["python","-m", "localllm.main"]
