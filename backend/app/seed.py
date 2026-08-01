"""Initialisation de l'espace administrateur (catégories, comptes, paramètres fiscaux)."""

from sqlalchemy.orm import Session

from app.config import parametres
from app.modeles import Utilisateur
from app.services.auth_service import creer_utilisateur, obtenir_utilisateur_par_email
from app.services.espace_utilisateur import initialiser_espace_utilisateur


def executer_seed(session: Session) -> None:
    if not parametres.admin_email or not parametres.admin_mot_de_passe:
        return

    admin = obtenir_utilisateur_par_email(session, parametres.admin_email)
    if admin is None:
        admin = creer_utilisateur(
            session,
            email=parametres.admin_email,
            mot_de_passe=parametres.admin_mot_de_passe,
            nom=parametres.admin_nom or "Administrateur",
        )
    initialiser_espace_utilisateur(session, admin.id)
