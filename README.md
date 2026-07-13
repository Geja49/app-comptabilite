# Comptabilité Taxi

Application web locale pour la comptabilité mensuelle d'une compagnie de taxi québécoise.

## Stack

- **Backend** : FastAPI + SQLAlchemy + PostgreSQL
- **Frontend** : Vue 3 + Vite + Tailwind CSS
- **Déploiement** : Docker Compose (local)

## Fonctionnalités

- Saisie journalière des revenus, dépenses et kilométrage
- Calculs automatiques TPS (5 %), TVQ (9,975 %), redevance gouvernementale (0,90 $/course)
- Sommaire annuel avec TPS/TVQ à remettre et dépenses proratées
- Dépenses récurrentes auto-générées
- Catégories de dépenses personnalisables
- Exports Excel (mensuel) et PDF (annuel pour comptable)
- Tableau de bord avec alertes

## Démarrage rapide

```bash
# Lancer l'application (Docker)
./lancer.sh

# Ou explicitement :
./lancer.sh docker    # Tout via Docker
./lancer.sh local     # PostgreSQL Docker + backend/frontend locaux
./lancer.sh arret     # Arrêter les services
./lancer.sh logs      # Voir les logs
```

```bash
# Copier la configuration (fait automatiquement par lancer.sh)
cp .env.example .env

# Lancer tous les services
docker-compose up -d --build

# Accéder à l'application
# Frontend : http://localhost:5173
# API : http://localhost:8000/docs
```

## Développement local (sans Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# PostgreSQL doit être démarré (voir docker compose up db)
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest tests/
```

## Structure des données

Chaque mois est une **période** distincte. Les données saisies alimentent automatiquement le sommaire annuel.

| Module | Saisie | Calculs automatiques |
|--------|--------|---------------------|
| Revenus | Date, courses, revenu brut, pourboires | Redevance, TPS, TVQ, total net |
| Dépenses | Date, fournisseur, catégorie, montant HT ou TTC | TPS payée, TVQ payée, total |
| Kilométrage | Date, odomètres, km pro | Km totaux, taux pro mensuel |
