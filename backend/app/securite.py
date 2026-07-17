import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import parametres

CHEMINS_PUBLICS = {"/api/sante"}


class MiddlewareCleApi(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        chemin = request.url.path.rstrip("/") or "/"
        # Santé API + fichiers frontend (hors /api) restent publics
        if request.method == "OPTIONS" or chemin in CHEMINS_PUBLICS or not chemin.startswith("/api"):
            return await call_next(request)

        attendu = parametres.api_cle
        if not attendu:
            return JSONResponse(
                status_code=503,
                content={"detail": "API_CLE non configurée sur le serveur"},
            )

        fourni = request.headers.get("X-API-Key") or ""
        if not fourni or not secrets.compare_digest(fourni, attendu):
            return JSONResponse(
                status_code=401,
                content={"detail": "Clé API manquante ou invalide"},
                headers={"WWW-Authenticate": "ApiKey"},
            )
        return await call_next(request)


class MiddlewareEnTetesSecurite(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        reponse = await call_next(request)
        reponse.headers["X-Content-Type-Options"] = "nosniff"
        reponse.headers["X-Frame-Options"] = "DENY"
        reponse.headers["Referrer-Policy"] = "no-referrer"
        reponse.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        reponse.headers["Cache-Control"] = "no-store"
        if parametres.est_production:
            reponse.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return reponse


class MiddlewareLimiteCorps(BaseHTTPMiddleware):
    """Refuse les requêtes dont Content-Length dépasse la limite configurée."""

    async def dispatch(self, request: Request, call_next) -> Response:
        contenu = request.headers.get("content-length")
        if contenu is not None:
            try:
                taille = int(contenu)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Content-Length invalide"})
            if taille > parametres.taille_max_corps:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Corps de requête trop volumineux"},
                )
        return await call_next(request)
