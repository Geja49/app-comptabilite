"""Authentification : mots de passe et jetons JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config import parametres
from app.modeles.utilisateur import Utilisateur

ALGORITHME_JWT = "HS256"


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verifier_mot_de_passe(mot_de_passe: str, empreinte: str) -> bool:
    try:
        return bcrypt.checkpw(mot_de_passe.encode("utf-8"), empreinte.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def secret_jwt() -> str:
    secret = parametres.jwt_secret or parametres.api_cle
    if not secret:
        raise RuntimeError("JWT_SECRET (ou API_CLE) non configuré")
    return secret


def creer_jeton(utilisateur: Utilisateur) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=parametres.jwt_duree_heures)
    charge = {
        "sub": str(utilisateur.id),
        "email": utilisateur.email,
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(charge, secret_jwt(), algorithm=ALGORITHME_JWT)


def decoder_jeton(jeton: str) -> dict | None:
    try:
        return jwt.decode(jeton, secret_jwt(), algorithms=[ALGORITHME_JWT])
    except jwt.PyJWTError:
        return None


def compter_utilisateurs(session: Session) -> int:
    return session.query(Utilisateur).count()


def trouver_par_email(session: Session, email: str) -> Utilisateur | None:
    return session.query(Utilisateur).filter_by(email=email.strip().lower()).first()


def creer_utilisateur(session: Session, email: str, mot_de_passe: str) -> Utilisateur:
    utilisateur = Utilisateur(
        email=email.strip().lower(),
        mot_de_passe_hash=hacher_mot_de_passe(mot_de_passe),
        actif=True,
    )
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    return utilisateur
