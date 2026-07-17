from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import parametres
from app.routeurs import categories, depenses_recurrentes, parametres_fiscaux, periodes, rapports

app = FastAPI(title="Comptabilité Taxi", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=parametres.liste_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.routeur)
app.include_router(depenses_recurrentes.routeur)
app.include_router(parametres_fiscaux.routeur)
app.include_router(periodes.routeur)
app.include_router(rapports.routeur)


@app.get("/api/sante")
def sante():
    return {"statut": "ok"}
