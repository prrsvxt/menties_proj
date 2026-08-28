FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.4.1

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --only main --no-interaction --no-ansi


FROM python:3.13-slim

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /app/.venv /app/.venv

COPY --chown=app:app src/ ./src
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app alembic/ ./alembic/

USER app

CMD ["python", "-m", "src.main"]