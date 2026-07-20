from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.dependances import obtenir_utilisateur_id
from app.modeles import CategorieDepense
from app.pagination import params_pagination
from app.schemas import CategorieDepenseCreate, CategorieDepenseReponse

routeur = APIRouter(prefix="/api/categories", tags=["categories"])


@routeur.get("", response_model=list[CategorieDepenseReponse])
def lister_categories(
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
    pagination: tuple[int, int] = Depends(params_pagination),
):
    decalage, limite = pagination
    return (
        session.query(CategorieDepense)
        .filter_by(utilisateur_id=utilisateur_id)
        .order_by(CategorieDepense.nom)
        .offset(decalage)
        .limit(limite)
        .all()
    )


@routeur.post("", response_model=CategorieDepenseReponse, status_code=201)
def ajouter_categorie(
    donnees: CategorieDepenseCreate,
    session: Session = Depends(obtenir_session),
    utilisateur_id: int = Depends(obtenir_utilisateur_id),
):
    existe = (
        session.query(CategorieDepense)
        .filter_by(utilisateur_id=utilisateur_id, nom=donnees.nom)
        .first()
    )
    if existe:
        raise HTTPException(status_code=400, detail="Cette catégorie existe déjà")
    categorie = CategorieDepense(utilisateur_id=utilisateur_id, nom=donnees.nom, est_systeme=False)
    session.add(categorie)
    session.commit()
    session.refresh(categorie)
    return categorie
