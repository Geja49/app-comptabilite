from decimal import Decimal

from app.config import parametres as config_app
from app.database import SessionLocale
from app.modeles import CategorieDepense, DepenseRecurrente, FrequenceDepenseRecurrente, ParametresFiscaux
from app.services import auth_service
from app.services.parametres_fiscaux_service import TAUX_DEFAUT
from app.services.tresorerie_service import assurer_comptes_par_defaut

CATEGORIES_SYSTEME = [
    "Essence/Énergie",
    "Assurance commerciale",
    "Entretien véhicule",
    "Location véhicule",
    "Nourriture",
    "Téléphone",
    "Permis et licences",
    "Autre",
]

ANNEE_DEFAUT = 2026
LOCATION_VEHICULE_JOURNALIERE = Decimal("110.00")
ESSENCE_VEHICULE_JOURNALIERE = Decimal("35.00")


def executer_seed():
    session = SessionLocale()
    try:
        for nom in CATEGORIES_SYSTEME:
            existe = session.query(CategorieDepense).filter_by(nom=nom).first()
            if not existe:
                session.add(CategorieDepense(nom=nom, est_systeme=True))
        session.flush()

        parametres = session.get(ParametresFiscaux, ANNEE_DEFAUT)
        if parametres is None:
            session.add(ParametresFiscaux(annee=ANNEE_DEFAUT, **TAUX_DEFAUT))

        categorie_location = session.query(CategorieDepense).filter_by(nom="Location véhicule").first()
        location = (
            session.query(DepenseRecurrente)
            .filter_by(fournisseur="Location véhicule")
            .first()
        )
        if location is None and categorie_location is not None:
            session.add(
                DepenseRecurrente(
                    fournisseur="Location véhicule",
                    categorie_id=categorie_location.id,
                    montant=LOCATION_VEHICULE_JOURNALIERE,
                    montant_ttc=True,
                    jour_du_mois=1,
                    frequence=FrequenceDepenseRecurrente.PAR_JOUR_TRAVAIL,
                    actif=True,
                )
            )
        elif location is not None:
            # Les montants récurrents sont déjà TTC (taxes incluses)
            location.montant_ttc = True
            if location.montant != LOCATION_VEHICULE_JOURNALIERE:
                location.montant = LOCATION_VEHICULE_JOURNALIERE

        # Toutes les récurrentes existantes : montants déjà TTC
        for recurrente in session.query(DepenseRecurrente).all():
            if not recurrente.montant_ttc:
                recurrente.montant_ttc = True

        # Compte admin initial (Render : ADMIN_EMAIL + ADMIN_MOT_DE_PASSE)
        if (
            config_app.admin_email
            and config_app.admin_mot_de_passe
            and auth_service.compter_utilisateurs(session) == 0
        ):
            auth_service.creer_utilisateur(
                session,
                config_app.admin_email,
                config_app.admin_mot_de_passe,
            )

        session.commit()
        assurer_comptes_par_defaut(session)
    finally:
        session.close()


if __name__ == "__main__":
    executer_seed()
