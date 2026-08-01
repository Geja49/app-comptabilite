from app.config import parametres as config_app
from app.database import SessionLocale
from app.services import auth_service
from app.services.espace_utilisateur import initialiser_espace_utilisateur


def executer_seed():
    """Crée le compte admin initial (via variables d'env) et son espace de données.

    Aucune donnée globale n'est créée : chaque utilisateur reçoit son propre
    espace (catégories, paramètres fiscaux, récurrente location, comptes)
    via initialiser_espace_utilisateur, appelée aussi à l'inscription normale.
    """
    session = SessionLocale()
    try:
        if config_app.admin_email and config_app.admin_mot_de_passe:
            utilisateur = auth_service.trouver_par_email(session, config_app.admin_email)
            if utilisateur is None:
                utilisateur = auth_service.creer_utilisateur(
                    session,
                    config_app.admin_email,
                    config_app.admin_mot_de_passe,
                )
            initialiser_espace_utilisateur(session, utilisateur.id)
    finally:
        session.close()


if __name__ == "__main__":
    executer_seed()
