#!/usr/bin/env bash
set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-docker}"

afficher_aide() {
  echo "Usage: ./lancer.sh [docker|local|arret|logs|aide]"
  echo ""
  echo "  docker  Lance l'application avec Docker (défaut)"
  echo "  local   Lance PostgreSQL via Docker, backend et frontend en local"
  echo "  arret   Arrête tous les services Docker"
  echo "  logs    Affiche les logs Docker en direct"
  echo "  aide    Affiche cette aide"
}

detecter_compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
  elif docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  else
    echo ""
  fi
}

compose_cmd() {
  local compose
  compose="$(detecter_compose)"
  if [[ "$compose" == "docker-compose" ]]; then
    echo "docker-compose -f docker-compose.yml"
  else
    echo "docker compose -f docker-compose.yml"
  fi
}

compose_local_db() {
  local base
  base="$(compose_cmd)"
  echo "$base -f docker-compose.local.yml"
}

nettoyer_conteneurs() {
  local compose_cmd_base
  compose_cmd_base="$(compose_cmd)"
  cd "$RACINE"
  # Supprime les conteneurs en échec d'un lancement précédent
  $compose_cmd_base down --remove-orphans 2>/dev/null || true
  docker rm -f app-comptabilite_db_1 2>/dev/null || true
}

lancer_docker() {
  local compose
  compose="$(detecter_compose)"
  if [[ -z "$compose" ]]; then
    echo "Erreur: Docker Compose n'est pas installé."
    exit 1
  fi

  if ! docker info >/dev/null 2>&1; then
    echo "Erreur: le démon Docker ne tourne pas. Démarrez Docker puis relancez."
    exit 1
  fi

  if [[ ! -f "$RACINE/.env" ]]; then
    cp "$RACINE/.env.example" "$RACINE/.env"
    echo "Fichier .env créé à partir de .env.example"
  fi

  cd "$RACINE"
  nettoyer_conteneurs
  echo "Construction et démarrage des services..."
  $(compose_cmd) up -d --build

  echo ""
  echo "Application démarrée."
  echo "  Frontend : http://localhost:5173"
  echo "  API      : http://localhost:8000/docs"
  echo ""
  echo "Pour voir les logs : ./lancer.sh logs"
  echo "Pour arrêter       : ./lancer.sh arret"
}

lancer_local() {
  if [[ ! -f "$RACINE/.env" ]]; then
    cp "$RACINE/.env.example" "$RACINE/.env"
    echo "Fichier .env créé à partir de .env.example"
  fi

  local compose
  compose="$(detecter_compose)"
  if [[ -n "$compose" ]] && docker info >/dev/null 2>&1; then
    echo "Démarrage de PostgreSQL via Docker (port 5433)..."
    cd "$RACINE"
    nettoyer_conteneurs
    $(compose_local_db) up -d db
    echo "Attente de PostgreSQL..."
    sleep 3
  else
    echo "Attention: PostgreSQL doit être accessible sur localhost:5433"
  fi

  # Backend
  if [[ ! -d "$RACINE/backend/venv" ]]; then
    echo "Création de l'environnement Python..."
    python3 -m venv "$RACINE/backend/venv"
  fi

  echo "Installation des dépendances backend..."
  "$RACINE/backend/venv/bin/pip" install -q -r "$RACINE/backend/requirements.txt"

  echo "Migrations et initialisation..."
  cd "$RACINE/backend"
  export DATABASE_URL="${DATABASE_URL:-postgresql://comptabilite:comptabilite@localhost:5433/comptabilite}"
  "$RACINE/backend/venv/bin/alembic" upgrade head
  "$RACINE/backend/venv/bin/python" -m app.seed

  echo "Démarrage du backend (port 8000)..."
  "$RACINE/backend/venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000 &
  PID_BACKEND=$!

  # Frontend
  if [[ ! -d "$RACINE/frontend/node_modules" ]]; then
    echo "Installation des dépendances frontend..."
    cd "$RACINE/frontend"
    npm install
  fi

  echo "Démarrage du frontend (port 5173)..."
  cd "$RACINE/frontend"
  npm run dev &
  PID_FRONTEND=$!

  echo ""
  echo "Application démarrée en mode local."
  echo "  Frontend : http://localhost:5173"
  echo "  API      : http://localhost:8000/docs"
  echo ""
  echo "Appuyez sur Ctrl+C pour arrêter."

  trap "kill $PID_BACKEND $PID_FRONTEND 2>/dev/null; exit" INT TERM
  wait
}

arreter() {
  if [[ -z "$(detecter_compose)" ]]; then
    echo "Erreur: Docker Compose n'est pas installé."
    exit 1
  fi
  cd "$RACINE"
  $(compose_cmd) down --remove-orphans
  docker rm -f app-comptabilite_db_1 app-comptabilite_backend_1 app-comptabilite_frontend_1 2>/dev/null || true
  echo "Services arrêtés."
}

afficher_logs() {
  if [[ -z "$(detecter_compose)" ]]; then
    echo "Erreur: Docker Compose n'est pas installé."
    exit 1
  fi
  cd "$RACINE"
  $(compose_cmd) logs -f
}

case "$MODE" in
  docker)
    lancer_docker
    ;;
  local)
    lancer_local
    ;;
  arret|stop)
    arreter
    ;;
  logs)
    afficher_logs
    ;;
  aide|-h|--help)
    afficher_aide
    ;;
  *)
    echo "Mode inconnu: $MODE"
    afficher_aide
    exit 1
    ;;
esac
