from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.modeles.utilisateur import Utilisateur
from app.schemas.auth import AuthStatutReponse, IdentifiantsAuth, JetonReponse, UtilisateurReponse
from app.services import auth_service

routeur = APIRouter(prefix="/api/auth", tags=["auth"])


def exiger_charge_jwt(requete: Request) -> dict:
    en_tete = requete.headers.get("Authorization") or ""
    if not en_tete.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentification requise")
    charge = auth_service.decoder_jeton(en_tete[7:].strip())
    if not charge or "sub" not in charge:
        raise HTTPException(status_code=401, detail="Session expirée ou invalide")
    return charge


@routeur.get("/statut", response_model=AuthStatutReponse)
def statut_auth(session: Session = Depends(obtenir_session)):
    return AuthStatutReponse(inscription_ouverte=auth_service.compter_utilisateurs(session) == 0)


@routeur.post("/inscription", response_model=JetonReponse, status_code=201)
def inscription(donnees: IdentifiantsAuth, session: Session = Depends(obtenir_session)):
    if auth_service.compter_utilisateurs(session) > 0:
        raise HTTPException(
            status_code=403,
            detail="L'inscription est fermée. Demandez un accès à l'administrateur.",
        )
    if auth_service.trouver_par_email(session, donnees.email):
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    utilisateur = auth_service.creer_utilisateur(session, donnees.email, donnees.mot_de_passe)
    return JetonReponse(jeton=auth_service.creer_jeton(utilisateur), email=utilisateur.email)


@routeur.post("/connexion", response_model=JetonReponse)
def connexion(donnees: IdentifiantsAuth, session: Session = Depends(obtenir_session)):
    utilisateur = auth_service.trouver_par_email(session, donnees.email)
    if (
        utilisateur is None
        or not utilisateur.actif
        or not auth_service.verifier_mot_de_passe(donnees.mot_de_passe, utilisateur.mot_de_passe_hash)
    ):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    return JetonReponse(jeton=auth_service.creer_jeton(utilisateur), email=utilisateur.email)


@routeur.get("/moi", response_model=UtilisateurReponse)
def moi(session: Session = Depends(obtenir_session), charge: dict = Depends(exiger_charge_jwt)):
    utilisateur = session.get(Utilisateur, int(charge["sub"]))
    if not utilisateur or not utilisateur.actif:
        raise HTTPException(status_code=401, detail="Session invalide")
    return utilisateur
