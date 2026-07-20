from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.dependances import obtenir_utilisateur_id
from app.modeles import MethodeTpsTvq
from app.schemas import ParametresFiscauxReponse, ParametresFiscauxUpdate
from app.services.parametres_fiscaux_service import obtenir_ou_creer_parametres_fiscaux

routeur = APIRouter(prefix="/api/parametres-fiscaux", tags=["parametres-fiscaux"])


@routeur.get("/{annee}", response_model=ParametresFiscauxReponse)
def obtenir_parametres(
    annee: int,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    if annee < 2000 or annee > 2100:
        raise HTTPException(status_code=400, detail="Année invalide")
    return obtenir_ou_creer_parametres_fiscaux(session, annee, utilisateur_id)


@routeur.put("/{annee}", response_model=ParametresFiscauxReponse)
def modifier_parametres(
    annee: int,
    donnees: ParametresFiscauxUpdate,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    if annee < 2000 or annee > 2100:
        raise HTTPException(status_code=400, detail="Année invalide")
    if donnees.methode_tps_tvq not in (MethodeTpsTvq.REGULIERE, MethodeTpsTvq.RAPIDE):
        raise HTTPException(status_code=400, detail="Méthode invalide")
    parametres = obtenir_ou_creer_parametres_fiscaux(session, annee, utilisateur_id)
    parametres.methode_tps_tvq = donnees.methode_tps_tvq
    session.commit()
    session.refresh(parametres)
    return parametres
