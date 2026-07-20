"""Initialisation de l'espace d'un nouvel utilisateur.

Au premier accès d'un compte, on crée ses données de départ : catégories
système, paramètres fiscaux de l'année en cours, dépense récurrente de
location véhicule et comptes de trésorerie par défaut.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modeles import CategorieDepense, DepenseRecurrente, FrequenceDepenseRecurrente
from app.services.parametres_fiscaux_service import obtenir_ou_creer_parametres_fiscaux
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

LOCATION_VEHICULE_JOURNALIERE = Decimal("110.00")


def initialiser_espace_utilisateur(session: Session, utilisateur_id: int) -> None:
    """Crée les données de départ d'un utilisateur (idempotent)."""
    for nom in CATEGORIES_SYSTEME:
        existe = session.query(CategorieDepense).filter_by(utilisateur_id=utilisateur_id, nom=nom).first()
        if not existe:
            session.add(CategorieDepense(utilisateur_id=utilisateur_id, nom=nom, est_systeme=True))
    session.flush()

    obtenir_ou_creer_parametres_fiscaux(session, date.today().year, utilisateur_id)

    categorie_location = (
        session.query(CategorieDepense).filter_by(utilisateur_id=utilisateur_id, nom="Location véhicule").first()
    )
    if categorie_location is not None:
        location = (
            session.query(DepenseRecurrente)
            .filter_by(utilisateur_id=utilisateur_id, fournisseur="Location véhicule")
            .first()
        )
        if location is None:
            session.add(
                DepenseRecurrente(
                    utilisateur_id=utilisateur_id,
                    fournisseur="Location véhicule",
                    categorie_id=categorie_location.id,
                    montant=LOCATION_VEHICULE_JOURNALIERE,
                    montant_ttc=True,
                    jour_du_mois=1,
                    frequence=FrequenceDepenseRecurrente.PAR_JOUR_TRAVAIL,
                    actif=True,
                )
            )

    session.commit()
    assurer_comptes_par_defaut(session, utilisateur_id)
