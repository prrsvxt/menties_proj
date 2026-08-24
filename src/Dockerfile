FROM python:3.13-rc-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY src/ ./src
COPY alembic.ini ./
COPY alembic/ ./alembic/

CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]