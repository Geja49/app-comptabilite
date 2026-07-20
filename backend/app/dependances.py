"""Dépendances FastAPI communes aux routeurs."""

from fastapi import HTTPException, Request


def obtenir_utilisateur_id(requete: Request) -> int:
    """Récupère l'utilisateur authentifié (posé par MiddlewareAuthentification)."""
    uid = getattr(requete.state, "utilisateur_id", None)
    if uid is None:
        raise HTTPException(status_code=401, detail="Authentification requise")
    return int(uid)
