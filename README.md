# Comptabilité Taxi

Application web pour la comptabilité mensuelle d'une compagnie de taxi québécoise.

## Stack

- **Backend** : FastAPI + SQLAlchemy + PostgreSQL
- **Frontend** : Vue 3 + Vite + Tailwind CSS
- **Auth** : email / mot de passe + JWT
- **Local** : Docker Compose ou SQLite
- **En ligne (gratuit)** : [Render](https://render.com) (app) + [Neon](https://neon.tech) (base de données)

## Fonctionnalités

- Connexion sécurisée (premier compte = admin, inscription ensuite fermée)
- Saisie journalière des revenus, dépenses et kilométrage
- Calculs automatiques TPS (5 %), TVQ (9,975 %), redevance gouvernementale (0,90 $/course)
- Sommaire annuel avec TPS/TVQ à remettre et dépenses proratées
- Dépenses récurrentes auto-générées
- Exports Excel (mensuel) et PDF (annuel)
- Méthodes fiscales régulière / rapide

## Publier en ligne (gratuit)

### 1. Base Neon

1. [console.neon.tech](https://console.neon.tech) → créer un projet
2. Copier la connection string (avec `sslmode=require`)

### 2. Application Render

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
2. Dépôt `app-comptabilite`
3. Variables :
   - `DATABASE_URL` = URI Neon
   - `CORS_ORIGINS` = `https://VOTRE-SERVICE.onrender.com`
   - `JWT_SECRET` = généré automatiquement
   - Optionnel : `ADMIN_EMAIL` + `ADMIN_MOT_DE_PASSE` pour créer le compte au démarrage
4. Après déploiement : ouvrir l’URL → **créer le compte** (si pas d’admin) ou **se connecter**

> Plan gratuit Render : endormissement après ~15 min d’inactivité.

## Démarrage rapide (local)

```bash
.\lancer.cmd
```

- Frontend : http://localhost:5173 → page Connexion
- API : http://localhost:8000/docs

## Tests

```bash
cd backend
pytest tests/
```
