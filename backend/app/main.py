from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import parametres
from app.routeurs import auth, categories, depenses_recurrentes, parametres_fiscaux, periodes, rapports, tresorerie
from app.securite import MiddlewareAuthentification, MiddlewareEnTetesSecurite, MiddlewareLimiteCorps

_docs = None if parametres.est_production else "/docs"
_redoc = None if parametres.est_production else "/redoc"
_openapi = None if parametres.est_production else "/openapi.json"

app = FastAPI(
    title="Comptabilité Taxi",
    version="1.0.0",
    docs_url=_docs,
    redoc_url=_redoc,
    openapi_url=_openapi,
)

# Ordre : le dernier ajouté s'exécute en premier sur la requête entrante
app.add_middleware(MiddlewareEnTetesSecurite)
app.add_middleware(MiddlewareLimiteCorps)
app.add_middleware(MiddlewareAuthentification)
app.add_middleware(
    CORSMiddleware,
    allow_origins=parametres.liste_cors,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth.routeur)
app.include_router(categories.routeur)
app.include_router(depenses_recurrentes.routeur)
app.include_router(parametres_fiscaux.routeur)
app.include_router(periodes.routeur)
app.include_router(rapports.routeur)
app.include_router(tresorerie.routeur)


@app.get("/api/sante")
def sante():
    """Santé publique (sans authentification) pour les sondes de déploiement."""
    return {"statut": "ok"}


# Frontend Vue compilé (même service en production)
CHEMIN_STATIQUE = Path(__file__).resolve().parent.parent / "statique"
if CHEMIN_STATIQUE.is_dir():
    assets = CHEMIN_STATIQUE / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{chemin_complet:path}")
    def servir_frontend(chemin_complet: str):
        if chemin_complet.startswith("api"):
            raise HTTPException(status_code=404, detail="Introuvable")
        candidat = CHEMIN_STATIQUE / chemin_complet
        if chemin_complet and candidat.is_file():
            return FileResponse(candidat)
        return FileResponse(CHEMIN_STATIQUE / "index.html")
