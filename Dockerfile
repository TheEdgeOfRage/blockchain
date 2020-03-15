FROM python:3.8-alpine AS builder

WORKDIR /app
ENV PATH="/root/.poetry/bin:$PATH"

RUN apk add --no-cache build-base libffi-dev curl \
	&& curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
	&& python -m venv .venv \
	&& poetry config virtualenvs.in-project true \
	&& .venv/bin/pip install --no-cache-dir -U pip setuptools

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root --no-interaction

COPY blockchain/ ./blockchain/


FROM python:3.8-alpine

EXPOSE 80
WORKDIR /app
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "80"]
ENV PATH="/app/.venv/bin:$PATH" \
	PYTHONUNBUFFERED=1

RUN apk add --no-cache libc-dev binutils

COPY run.py ./
COPY --from=builder /app/ ./
