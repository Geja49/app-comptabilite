# Image de production : frontend + API sur un seul service (Render gratuit)
FROM node:22.17.1-alpine3.22 AS frontend

WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
# Même origine en prod : URL API relative
ENV VITE_API_URL=
RUN npm run build

FROM python:3.12.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --no-create-home app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend --chown=app:app /frontend/dist ./statique

USER app

ENV ENVIRONNEMENT=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
