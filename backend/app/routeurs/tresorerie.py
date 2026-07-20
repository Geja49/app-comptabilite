from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.dependances import obtenir_utilisateur_id
from app.pagination import params_pagination
from app.services import tresorerie_service

routeur = APIRouter(prefix="/api/tresorerie", tags=["tresorerie"])


class CompteTresorerieReponse(BaseModel):
    id: int
    nom: str
    type_compte: str
    solde_ouverture: Decimal
    solde_actuel: Decimal
    actif: bool


class ResumeTresorerieReponse(BaseModel):
    comptes: list[CompteTresorerieReponse]
    total_caisse: Decimal
    total_banque: Decimal
    total_tresorerie: Decimal


class OperationTresorerieCreate(BaseModel):
    date_operation: date
    type_operation: str = Field(
        pattern="^(encaissement|depot|retrait|paiement|transfert|ajustement)$"
    )
    compte_id: int
    compte_contrepartie_id: int | None = None
    montant: Decimal = Field(gt=0)
    est_entree: bool | None = None
    libelle: str = Field(min_length=1, max_length=255)
    reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    revenu_id: int | None = None


class OperationTresorerieReponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_operation: date
    type_operation: str
    compte_id: int
    compte_nom: str
    compte_contrepartie_id: int | None = None
    compte_contrepartie_nom: str | None = None
    montant: Decimal
    est_entree: bool
    libelle: str
    reference: str | None = None
    notes: str | None = None
    revenu_id: int | None = None


class CompteTresorerieUpdateOuverture(BaseModel):
    solde_ouverture: Decimal = Field(ge=0)


@routeur.get("/resume", response_model=ResumeTresorerieReponse)
def obtenir_resume(
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    tresorerie_service.assurer_comptes_par_defaut(session, utilisateur_id)
    return tresorerie_service.resume_tresorerie(session, utilisateur_id)


@routeur.get("/operations", response_model=list[OperationTresorerieReponse])
def lister_operations(
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
    pagination: tuple[int, int] = Depends(params_pagination),
    compte_id: int | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
):
    tresorerie_service.assurer_comptes_par_defaut(session, utilisateur_id)
    decalage, limite = pagination
    return tresorerie_service.lister_operations(
        session,
        utilisateur_id,
        compte_id=compte_id,
        date_debut=date_debut,
        date_fin=date_fin,
        decalage=decalage,
        limite=limite,
    )


@routeur.post("/operations", response_model=list[OperationTresorerieReponse], status_code=201)
def creer_operation(
    donnees: OperationTresorerieCreate,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    tresorerie_service.assurer_comptes_par_defaut(session, utilisateur_id)
    return tresorerie_service.creer_operation(
        session,
        utilisateur_id,
        date_operation=donnees.date_operation,
        type_operation=donnees.type_operation,
        compte_id=donnees.compte_id,
        compte_contrepartie_id=donnees.compte_contrepartie_id,
        montant=donnees.montant,
        est_entree=donnees.est_entree,
        libelle=donnees.libelle,
        reference=donnees.reference,
        notes=donnees.notes,
        revenu_id=donnees.revenu_id,
    )


@routeur.delete("/operations/{operation_id}", status_code=204)
def supprimer_operation(
    operation_id: int,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    tresorerie_service.supprimer_operation(session, operation_id, utilisateur_id)


@routeur.put("/comptes/{compte_id}/solde-ouverture", response_model=CompteTresorerieReponse)
def modifier_solde_ouverture(
    compte_id: int,
    donnees: CompteTresorerieUpdateOuverture,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    compte = tresorerie_service._exiger_compte(session, compte_id, utilisateur_id)
    compte.solde_ouverture = donnees.solde_ouverture
    session.commit()
    solde = tresorerie_service.calculer_solde(session, compte)
    return CompteTresorerieReponse(
        id=compte.id,
        nom=compte.nom,
        type_compte=compte.type_compte if isinstance(compte.type_compte, str) else compte.type_compte.value,
        solde_ouverture=compte.solde_ouverture,
        solde_actuel=solde,
        actif=compte.actif,
    )
