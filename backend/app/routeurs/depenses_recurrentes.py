from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.dependances import obtenir_utilisateur_id
from app.modeles import CategorieDepense, DepenseRecurrente
from app.pagination import params_pagination
from app.schemas import DepenseRecurrenteCreate, DepenseRecurrenteReponse, DepenseRecurrenteUpdate

routeur = APIRouter(prefix="/api/depenses-recurrentes", tags=["depenses-recurrentes"])


def _vers_reponse(recurrente: DepenseRecurrente) -> DepenseRecurrenteReponse:
    return DepenseRecurrenteReponse(
        id=recurrente.id,
        fournisseur=recurrente.fournisseur,
        categorie_id=recurrente.categorie_id,
        categorie_nom=recurrente.categorie.nom,
        montant=recurrente.montant,
        montant_ttc=recurrente.montant_ttc,
        jour_du_mois=recurrente.jour_du_mois,
        frequence=recurrente.frequence,
        actif=recurrente.actif,
    )


def _exiger_categorie(session: Session, categorie_id: int, utilisateur_id: int) -> CategorieDepense:
    categorie = (
        session.query(CategorieDepense)
        .filter_by(id=categorie_id, utilisateur_id=utilisateur_id)
        .first()
    )
    if not categorie:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    return categorie


@routeur.get("", response_model=list[DepenseRecurrenteReponse])
def lister_recurrentes(
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
    pagination: tuple[int, int] = Depends(params_pagination),
):
    decalage, limite = pagination
    recurrentes = (
        session.query(DepenseRecurrente)
        .filter_by(utilisateur_id=utilisateur_id)
        .order_by(DepenseRecurrente.fournisseur)
        .offset(decalage)
        .limit(limite)
        .all()
    )
    return [_vers_reponse(r) for r in recurrentes]


@routeur.post("", response_model=DepenseRecurrenteReponse, status_code=201)
def creer_recurrente(
    donnees: DepenseRecurrenteCreate,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    _exiger_categorie(session, donnees.categorie_id, utilisateur_id)
    recurrente = DepenseRecurrente(utilisateur_id=utilisateur_id, **donnees.model_dump())
    session.add(recurrente)
    session.commit()
    session.refresh(recurrente)
    return _vers_reponse(recurrente)


@routeur.put("/{recurrente_id}", response_model=DepenseRecurrenteReponse)
def modifier_recurrente(
    recurrente_id: int,
    donnees: DepenseRecurrenteUpdate,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    recurrente = session.get(DepenseRecurrente, recurrente_id)
    if not recurrente or recurrente.utilisateur_id != utilisateur_id:
        raise HTTPException(status_code=404, detail="Dépense récurrente introuvable")
    _exiger_categorie(session, donnees.categorie_id, utilisateur_id)
    for cle, valeur in donnees.model_dump().items():
        setattr(recurrente, cle, valeur)
    session.commit()
    session.refresh(recurrente)
    return _vers_reponse(recurrente)


@routeur.delete("/{recurrente_id}", status_code=204)
def supprimer_recurrente(
    recurrente_id: int,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    recurrente = session.get(DepenseRecurrente, recurrente_id)
    if not recurrente or recurrente.utilisateur_id != utilisateur_id:
        raise HTTPException(status_code=404, detail="Dépense récurrente introuvable")
    session.delete(recurrente)
    session.commit()
