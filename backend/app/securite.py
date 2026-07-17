from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import parametres
from app.services import auth_service

CHEMINS_PUBLICS = {
    "/api/sante",
    "/api/auth/connexion",
    "/api/auth/inscription",
    "/api/auth/statut",
}


class MiddlewareAuthentification(BaseHTTPMiddleware):
    """Protège les routes /api avec un jeton JWT Bearer."""

    async def dispatch(self, request: Request, call_next) -> Response:
        chemin = request.url.path.rstrip("/") or "/"
        if request.method == "OPTIONS" or chemin in CHEMINS_PUBLICS or not chemin.startswith("/api"):
            return await call_next(request)

        try:
            auth_service.secret_jwt()
        except RuntimeError:
            return JSONResponse(
                status_code=503,
                content={"detail": "JWT_SECRET non configuré sur le serveur"},
            )

        en_tete = request.headers.get("Authorization") or ""
        if not en_tete.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentification requise"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        charge = auth_service.decoder_jeton(en_tete[7:].strip())
        if not charge or "sub" not in charge:
            return JSONResponse(
                status_code=401,
                content={"detail": "Session expirée ou invalide"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.utilisateur_id = int(charge["sub"])
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
