from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modeles import CategorieDepense, Depense, DepenseRecurrente, EntreeKilometrage, Periode, Revenu
from app.services import calculs


def obtenir_ou_creer_periode(session: Session, annee: int, mois: int) -> Periode:
    periode = session.query(Periode).filter_by(annee=annee, mois=mois).first()
    if periode is None:
        periode = Periode(annee=annee, mois=mois)
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


def generer_depenses_recurrentes(session: Session, periode: Periode) -> list[Depense]:
    recurrentes = session.query(DepenseRecurrente).filter_by(actif=True).all()
    creees: list[Depense] = []
    for recurrente in recurrentes:
        existe = (
            session.query(Depense)
            .filter_by(periode_id=periode.id, depense_recurrente_id=recurrente.id)
            .first()
        )
        if existe:
            continue
        jour = min(recurrente.jour_du_mois, 28)
        depense = Depense(
            periode_id=periode.id,
            date=date(periode.annee, periode.mois, jour),
            fournisseur=recurrente.fournisseur,
            categorie_id=recurrente.categorie_id,
            montant_ht=Decimal("0"),
            saisie_ttc=recurrente.montant_ttc,
            montant_saisi=recurrente.montant,
            depense_recurrente_id=recurrente.id,
        )
        taxes = (
            calculs.calculer_taxes_depuis_ttc(recurrente.montant)
            if recurrente.montant_ttc
            else calculs.calculer_taxes_depuis_ht(recurrente.montant)
        )
        depense.montant_ht = taxes["montant_ht"]
        session.add(depense)
        creees.append(depense)
    if creees:
        session.commit()
        for depense in creees:
            session.refresh(depense)
    return creees


def obtenir_donnees_periode(session: Session, annee: int, mois: int) -> dict:
    periode = obtenir_ou_creer_periode(session, annee, mois)
    revenus = [construire_revenu_calcule(r) for r in sorted(periode.revenus, key=lambda x: x.date)]
    depenses = [construire_depense_calculee(d) for d in sorted(periode.depenses, key=lambda x: x.date)]
    km_entrees = [construire_km_calcule(e) for e in sorted(periode.entrees_kilometrage, key=lambda x: x.date)]
    km_agrege = calculs.agreger_kilometrage(km_entrees) if km_entrees else {
        "km_totaux_mois": Decimal("0"),
        "km_pro_mois": Decimal("0"),
        "taux_pro": Decimal("0"),
    }
    sommaire = calculs.calculer_sommaire_mensuel(revenus, depenses, km_agrege["taux_pro"])
    return {
        "periode": {"id": periode.id, "annee": annee, "mois": mois, "est_passee": est_periode_passee(annee, mois)},
        "revenus": revenus,
        "depenses": depenses,
        "kilometrage": {"entrees": km_entrees, "totaux": km_agrege},
        "sommaire": sommaire,
    }
