from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modeles import (
    Depense,
    DepenseRecurrente,
    EntreeKilometrage,
    FrequenceDepenseRecurrente,
    Periode,
    Revenu,
)
from app.services import calculs, impots
from app.services.parametres_fiscaux_service import obtenir_ou_creer_parametres_fiscaux
from app.pagination import LIMITE_MAX


def obtenir_ou_creer_periode(session: Session, annee: int, mois: int, utilisateur_id: int) -> Periode:
    periode = session.query(Periode).filter_by(annee=annee, mois=mois, utilisateur_id=utilisateur_id).first()
    if periode is None:
        periode = Periode(annee=annee, mois=mois, utilisateur_id=utilisateur_id)
        session.add(periode)
        session.commit()
        session.refresh(periode)
    return periode


def valider_date_dans_periode(date_saisie: date, annee: int, mois: int) -> None:
    if date_saisie.year != annee or date_saisie.month != mois:
        raise ValueError("La date doit appartenir à la période sélectionnée")


def est_periode_passee(annee: int, mois: int) -> bool:
    aujourd_hui = date.today()
    return (annee, mois) < (aujourd_hui.year, aujourd_hui.month)


def construire_depense_calculee(depense: Depense) -> dict:
    if depense.saisie_ttc:
        taxes = calculs.calculer_taxes_depuis_ttc(depense.montant_saisi)
    else:
        taxes = calculs.calculer_taxes_depuis_ht(depense.montant_saisi)
    return {
        "id": depense.id,
        "date": depense.date,
        "fournisseur": depense.fournisseur,
        "categorie_id": depense.categorie_id,
        "categorie_nom": depense.categorie.nom if depense.categorie else "",
        "saisie_ttc": depense.saisie_ttc,
        "montant_saisi": depense.montant_saisi,
        "montant_ht": taxes["montant_ht"],
        "tps": taxes["tps"],
        "tvq": taxes["tvq"],
        "montant_total": taxes["montant_total"],
        "est_recurrente": depense.depense_recurrente_id is not None,
        "depense_recurrente_id": depense.depense_recurrente_id,
    }


def construire_revenu_calcule(revenu: Revenu) -> dict:
    calc = calculs.calculer_revenu(revenu.nombre_courses, revenu.revenu_brut, revenu.pourboires)
    return {"id": revenu.id, "date": revenu.date, **calc}


def construire_km_calcule(entree: EntreeKilometrage) -> dict:
    calc = calculs.calculer_kilometrage_jour(entree.odometre_debut, entree.odometre_fin, entree.km_professionnels)
    return {
        "id": entree.id,
        "date": entree.date,
        "odometre_debut": entree.odometre_debut,
        "odometre_fin": entree.odometre_fin,
        **calc,
    }


def _creer_depense_depuis_recurrente(
    session: Session,
    periode: Periode,
    recurrente: DepenseRecurrente,
    date_depense: date,
) -> Depense:
    taxes = (
        calculs.calculer_taxes_depuis_ttc(recurrente.montant)
        if recurrente.montant_ttc
        else calculs.calculer_taxes_depuis_ht(recurrente.montant)
    )
    depense = Depense(
        periode_id=periode.id,
        date=date_depense,
        fournisseur=recurrente.fournisseur,
        categorie_id=recurrente.categorie_id,
        montant_ht=taxes["montant_ht"],
        saisie_ttc=recurrente.montant_ttc,
        montant_saisi=recurrente.montant,
        depense_recurrente_id=recurrente.id,
    )
    session.add(depense)
    return depense


def generer_depenses_recurrentes(session: Session, periode: Periode) -> list[Depense]:
    """Génère les dépenses manquantes selon la fréquence de chaque récurrente.

    - mensuelle : une dépense par mois
    - par_jour_travail : une dépense par jour où un revenu est saisi
    """
    recurrentes = (
        session.query(DepenseRecurrente)
        .filter_by(actif=True, utilisateur_id=periode.utilisateur_id)
        .limit(LIMITE_MAX)
        .all()
    )
    creees: list[Depense] = []
    dates_travail = sorted({revenu.date for revenu in periode.revenus})

    for recurrente in recurrentes:
        if recurrente.frequence == FrequenceDepenseRecurrente.PAR_JOUR_TRAVAIL:
            for date_travail in dates_travail:
                existe = (
                    session.query(Depense)
                    .filter_by(
                        periode_id=periode.id,
                        depense_recurrente_id=recurrente.id,
                        date=date_travail,
                    )
                    .first()
                )
                if existe:
                    continue
                creees.append(
                    _creer_depense_depuis_recurrente(session, periode, recurrente, date_travail)
                )
            continue

        existe = (
            session.query(Depense)
            .filter_by(periode_id=periode.id, depense_recurrente_id=recurrente.id)
            .first()
        )
        if existe:
            continue
        jour = min(recurrente.jour_du_mois, 28)
        creees.append(
            _creer_depense_depuis_recurrente(
                session, periode, recurrente, date(periode.annee, periode.mois, jour)
            )
        )

    if creees:
        session.commit()
        for depense in creees:
            session.refresh(depense)
    return creees


def obtenir_donnees_periode(session: Session, annee: int, mois: int, utilisateur_id: int) -> dict:
    periode = obtenir_ou_creer_periode(session, annee, mois, utilisateur_id)
    parametres = obtenir_ou_creer_parametres_fiscaux(session, annee, utilisateur_id)
    revenus = [construire_revenu_calcule(r) for r in sorted(periode.revenus, key=lambda x: x.date)]
    depenses = [construire_depense_calculee(d) for d in sorted(periode.depenses, key=lambda x: x.date)]
    km_entrees = [construire_km_calcule(e) for e in sorted(periode.entrees_kilometrage, key=lambda x: x.date)]
    km_agrege = calculs.agreger_kilometrage(km_entrees) if km_entrees else {
        "km_totaux_mois": Decimal("0"),
        "km_pro_mois": Decimal("0"),
        "taux_pro": Decimal("0"),
    }
    sommaire = impots.calculer_sommaire_mensuel(
        revenus,
        depenses,
        km_agrege["taux_pro"],
        methode=parametres.methode_tps_tvq,
        tps_taux_rapide=parametres.tps_taux_rapide,
        tvq_taux_rapide=parametres.tvq_taux_rapide,
    )
    return {
        "periode": {"id": periode.id, "annee": annee, "mois": mois, "est_passee": est_periode_passee(annee, mois)},
        "revenus": revenus,
        "depenses": depenses,
        "kilometrage": {"entrees": km_entrees, "totaux": km_agrege},
        "sommaire": sommaire,
        "parametres_fiscaux": parametres,
    }
