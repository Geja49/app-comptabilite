from decimal import Decimal

from sqlalchemy.orm import Session

from app.modeles import MethodeTpsTvq, ParametresFiscaux

TAUX_DEFAUT = {
    "methode_tps_tvq": MethodeTpsTvq.REGULIERE.value,
    "tps_taux_reguliere": Decimal("0.05"),
    "tvq_taux_reguliere": Decimal("0.09975"),
    "tps_taux_rapide": Decimal("0.036"),
    "tvq_taux_rapide": Decimal("0.066"),
    "rabais_rapide_taux": Decimal("0.01"),
    "rabais_rapide_plafond": Decimal("30000"),
    "redevance_par_course": Decimal("0.90"),
}


def obtenir_ou_creer_parametres_fiscaux(session: Session, annee: int, utilisateur_id: int) -> ParametresFiscaux:
    parametres = session.get(ParametresFiscaux, (utilisateur_id, annee))
    if parametres is None:
        parametres = ParametresFiscaux(utilisateur_id=utilisateur_id, annee=annee, **TAUX_DEFAUT)
        session.add(parametres)
        session.commit()
        session.refresh(parametres)
    return parametres
