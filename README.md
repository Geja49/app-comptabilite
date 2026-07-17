# Comptabilité Taxi

Application web pour la comptabilité mensuelle d'une compagnie de taxi québécoise.

## Stack

- **Backend** : FastAPI + SQLAlchemy + PostgreSQL
- **Frontend** : Vue 3 + Vite + Tailwind CSS
- **Local** : Docker Compose ou SQLite
- **En ligne (gratuit)** : [Render](https://render.com) (app) + [Neon](https://neon.tech) (base de données)

## Fonctionnalités

- Saisie journalière des revenus, dépenses et kilométrage
- Calculs automatiques TPS (5 %), TVQ (9,975 %), redevance gouvernementale (0,90 $/course)
- Sommaire annuel avec TPS/TVQ à remettre et dépenses proratées
- Dépenses récurrentes auto-générées
- Catégories de dépenses personnalisables
- Exports Excel (mensuel) et PDF (annuel pour comptable)
- Tableau de bord avec alertes
- Méthodes fiscales régulière / rapide

## Publier en ligne (gratuit)

### 1. Base de données Neon (gratuit)

1. Créer un compte sur [console.neon.tech](https://console.neon.tech)
2. Créer un projet → copier la **connection string** PostgreSQL
3. Garder `sslmode=require` dans l’URL

### 2. Application sur Render (gratuit)

1. Pousser ce dépôt sur GitHub
2. Sur [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
3. Sélectionner le dépôt `app-comptabilite` (fichier `render.yaml`)
4. Renseigner les variables :
   - `DATABASE_URL` = URI Neon
   - `CORS_ORIGINS` = `https://VOTRE-SERVICE.onrender.com` (ou laisser vide si même origine)
   - `API_CLE` est générée automatiquement — **copiez-la** dans Render → Environment
5. Déployer, puis ouvrir l’URL Render et coller la même `API_CLE` dans l’écran « Clé d’accès »

> Le plan gratuit Render endort le service après ~15 min d’inactivité (premier chargement plus lent).

## Démarrage rapide (local)

```bash
# Windows
.\lancer.cmd

# Ou Docker
docker compose up -d --build
```

- Frontend : http://localhost:5173
- API : http://localhost:8000/docs

## Développement local (sans Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
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
