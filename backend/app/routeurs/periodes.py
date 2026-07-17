from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.modeles import Depense, EntreeKilometrage, Revenu
from app.pagination import appliquer_pagination, params_pagination
from app.schemas import (
    DepenseCreate,
    DepenseReponse,
    DepenseUpdate,
    EntreeKilometrageCreate,
    EntreeKilometrageReponse,
    EntreeKilometrageUpdate,
    RevenuCreate,
    RevenuReponse,
    RevenuUpdate,
)
from app.services import calculs
from app.services.periode_service import (
    construire_depense_calculee,
    construire_km_calcule,
    construire_revenu_calcule,
    est_periode_passee,
    generer_depenses_recurrentes,
    obtenir_donnees_periode,
    obtenir_ou_creer_periode,
    valider_date_dans_periode,
)

routeur = APIRouter(prefix="/api/periodes/{annee}/{mois}", tags=["periodes"])


def _verifier_periode(annee: int, mois: int):
    if mois < 1 or mois > 12:
        raise HTTPException(status_code=400, detail="Le mois doit être entre 1 et 12")


def _verifier_modification_passee(annee: int, mois: int, confirme: bool):
    if est_periode_passee(annee, mois) and not confirme:
        raise HTTPException(
            status_code=409,
            detail="Vous modifiez des données d'un mois passé. Confirmez pour continuer.",
        )


def _exiger_appartenance_periode(entite, periode, detail: str = "Ressource introuvable"):
    if not entite or entite.periode_id != periode.id:
        raise HTTPException(status_code=404, detail=detail)


@routeur.post("", status_code=201)
def creer_periode(annee: int, mois: int, session: Session = Depends(obtenir_session)):
    _verifier_periode(annee, mois)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    return {"id": periode.id, "annee": annee, "mois": mois}


@routeur.get("")
def obtenir_periode(annee: int, mois: int, session: Session = Depends(obtenir_session)):
    _verifier_periode(annee, mois)
    return obtenir_donnees_periode(session, annee, mois)


@routeur.post("/generer-recurrentes")
def generer_recurrentes(annee: int, mois: int, session: Session = Depends(obtenir_session)):
    _verifier_periode(annee, mois)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    creees = generer_depenses_recurrentes(session, periode)
    return {"generees": len(creees)}


@routeur.get("/revenus", response_model=list[RevenuReponse])
def lister_revenus(
    annee: int,
    mois: int,
    session: Session = Depends(obtenir_session),
    pagination: tuple[int, int] = Depends(params_pagination),
):
    _verifier_periode(annee, mois)
    donnees = obtenir_donnees_periode(session, annee, mois)
    decalage, limite = pagination
    return appliquer_pagination(donnees["revenus"], decalage, limite)


@routeur.post("/revenus", response_model=RevenuReponse, status_code=201)
def ajouter_revenu(annee: int, mois: int, donnees: RevenuCreate, session: Session = Depends(obtenir_session)):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, donnees.confirmer_modification_passee)
    valider_date_dans_periode(donnees.date, annee, mois)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    revenu = Revenu(
        periode_id=periode.id,
        date=donnees.date,
        nombre_courses=donnees.nombre_courses,
        revenu_brut=donnees.revenu_brut,
        pourboires=donnees.pourboires,
    )
    session.add(revenu)
    session.commit()
    session.refresh(revenu)
    # Location véhicule et autres dépenses « par jour de travail »
    generer_depenses_recurrentes(session, periode)
    return construire_revenu_calcule(revenu)


@routeur.put("/revenus/{revenu_id}", response_model=RevenuReponse)
def modifier_revenu(
    annee: int, mois: int, revenu_id: int, donnees: RevenuUpdate, session: Session = Depends(obtenir_session)
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, donnees.confirmer_modification_passee)
    valider_date_dans_periode(donnees.date, annee, mois)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    revenu = session.get(Revenu, revenu_id)
    _exiger_appartenance_periode(revenu, periode, "Revenu introuvable")
    revenu.date = donnees.date
    revenu.nombre_courses = donnees.nombre_courses
    revenu.revenu_brut = donnees.revenu_brut
    revenu.pourboires = donnees.pourboires
    session.commit()
    session.refresh(revenu)
    return construire_revenu_calcule(revenu)


@routeur.delete("/revenus/{revenu_id}", status_code=204)
def supprimer_revenu(
    annee: int, mois: int, revenu_id: int, confirmer_modification_passee: bool = False,
    session: Session = Depends(obtenir_session),
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, confirmer_modification_passee)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    revenu = session.get(Revenu, revenu_id)
    _exiger_appartenance_periode(revenu, periode, "Revenu introuvable")
    session.delete(revenu)
    session.commit()


@routeur.get("/depenses", response_model=list[DepenseReponse])
def lister_depenses(
    annee: int,
    mois: int,
    session: Session = Depends(obtenir_session),
    pagination: tuple[int, int] = Depends(params_pagination),
):
    _verifier_periode(annee, mois)
    decalage, limite = pagination
    return appliquer_pagination(
        obtenir_donnees_periode(session, annee, mois)["depenses"],
        decalage,
        limite,
    )


@routeur.post("/depenses", response_model=DepenseReponse, status_code=201)
def ajouter_depense(annee: int, mois: int, donnees: DepenseCreate, session: Session = Depends(obtenir_session)):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, donnees.confirmer_modification_passee)
    valider_date_dans_periode(donnees.date, annee, mois)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    taxes = (
        calculs.calculer_taxes_depuis_ttc(donnees.montant_saisi)
        if donnees.saisie_ttc
        else calculs.calculer_taxes_depuis_ht(donnees.montant_saisi)
    )
    depense = Depense(
        periode_id=periode.id,
        date=donnees.date,
        fournisseur=donnees.fournisseur,
        categorie_id=donnees.categorie_id,
        montant_ht=taxes["montant_ht"],
        saisie_ttc=donnees.saisie_ttc,
        montant_saisi=donnees.montant_saisi,
    )
    session.add(depense)
    session.commit()
    session.refresh(depense)
    return construire_depense_calculee(depense)


@routeur.put("/depenses/{depense_id}", response_model=DepenseReponse)
def modifier_depense(
    annee: int, mois: int, depense_id: int, donnees: DepenseUpdate, session: Session = Depends(obtenir_session)
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, donnees.confirmer_modification_passee)
    valider_date_dans_periode(donnees.date, annee, mois)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    depense = session.get(Depense, depense_id)
    _exiger_appartenance_periode(depense, periode, "Dépense introuvable")
    taxes = (
        calculs.calculer_taxes_depuis_ttc(donnees.montant_saisi)
        if donnees.saisie_ttc
        else calculs.calculer_taxes_depuis_ht(donnees.montant_saisi)
    )
    depense.date = donnees.date
    depense.fournisseur = donnees.fournisseur
    depense.categorie_id = donnees.categorie_id
    depense.montant_ht = taxes["montant_ht"]
    depense.saisie_ttc = donnees.saisie_ttc
    depense.montant_saisi = donnees.montant_saisi
    session.commit()
    session.refresh(depense)
    return construire_depense_calculee(depense)


@routeur.delete("/depenses/{depense_id}", status_code=204)
def supprimer_depense(
    annee: int, mois: int, depense_id: int, confirmer_modification_passee: bool = False,
    session: Session = Depends(obtenir_session),
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, confirmer_modification_passee)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    depense = session.get(Depense, depense_id)
    _exiger_appartenance_periode(depense, periode, "Dépense introuvable")
    session.delete(depense)
    session.commit()


@routeur.get("/kilometrage")
def lister_kilometrage(
    annee: int,
    mois: int,
    session: Session = Depends(obtenir_session),
    pagination: tuple[int, int] = Depends(params_pagination),
):
    _verifier_periode(annee, mois)
    decalage, limite = pagination
    return appliquer_pagination(
        obtenir_donnees_periode(session, annee, mois)["kilometrage"],
        decalage,
        limite,
    )


@routeur.post("/kilometrage", response_model=EntreeKilometrageReponse, status_code=201)
def ajouter_kilometrage(
    annee: int, mois: int, donnees: EntreeKilometrageCreate, session: Session = Depends(obtenir_session)
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, donnees.confirmer_modification_passee)
    valider_date_dans_periode(donnees.date, annee, mois)
    if donnees.odometre_fin < donnees.odometre_debut:
        raise HTTPException(status_code=400, detail="L'odomètre de fin doit être supérieur au début")
    if donnees.km_professionnels > (donnees.odometre_fin - donnees.odometre_debut):
        raise HTTPException(status_code=400, detail="Les km professionnels ne peuvent dépasser le total du jour")
    periode = obtenir_ou_creer_periode(session, annee, mois)
    entree = EntreeKilometrage(
        periode_id=periode.id,
        date=donnees.date,
        odometre_debut=donnees.odometre_debut,
        odometre_fin=donnees.odometre_fin,
        km_professionnels=donnees.km_professionnels,
    )
    session.add(entree)
    session.commit()
    session.refresh(entree)
    return construire_km_calcule(entree)


@routeur.put("/kilometrage/{entree_id}", response_model=EntreeKilometrageReponse)
def modifier_kilometrage(
    annee: int, mois: int, entree_id: int, donnees: EntreeKilometrageUpdate,
    session: Session = Depends(obtenir_session),
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, donnees.confirmer_modification_passee)
    valider_date_dans_periode(donnees.date, annee, mois)
    if donnees.odometre_fin < donnees.odometre_debut:
        raise HTTPException(status_code=400, detail="L'odomètre de fin doit être supérieur au début")
    periode = obtenir_ou_creer_periode(session, annee, mois)
    entree = session.get(EntreeKilometrage, entree_id)
    _exiger_appartenance_periode(entree, periode, "Entrée kilométrage introuvable")
    entree.date = donnees.date
    entree.odometre_debut = donnees.odometre_debut
    entree.odometre_fin = donnees.odometre_fin
    entree.km_professionnels = donnees.km_professionnels
    session.commit()
    session.refresh(entree)
    return construire_km_calcule(entree)


@routeur.delete("/kilometrage/{entree_id}", status_code=204)
def supprimer_kilometrage(
    annee: int, mois: int, entree_id: int, confirmer_modification_passee: bool = False,
    session: Session = Depends(obtenir_session),
):
    _verifier_periode(annee, mois)
    _verifier_modification_passee(annee, mois, confirmer_modification_passee)
    periode = obtenir_ou_creer_periode(session, annee, mois)
    entree = session.get(EntreeKilometrage, entree_id)
    _exiger_appartenance_periode(entree, periode, "Entrée kilométrage introuvable")
    session.delete(entree)
    session.commit()
