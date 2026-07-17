# Image épinglée (pas :latest) pour éviter les dérives silencieuses
FROM python:3.12.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --no-create-home app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .

USER app

ENV ENVIRONNEMENT=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
