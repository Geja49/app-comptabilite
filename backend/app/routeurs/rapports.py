from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.modeles import DepenseRecurrente
from app.schemas import AlerteReponse, SommaireAnnuelReponse, SommaireMensuelReponse, TableauDeBordReponse, PeriodeReponse
from app.services.export_excel import NOMS_MOIS, exporter_mois_excel
from app.services.export_pdf import exporter_annee_pdf
from app.services.periode_service import est_periode_passee, obtenir_donnees_periode

routeur = APIRouter(tags=["rapports"])


def _sommaire_mensuel(mois: int, donnees: dict) -> SommaireMensuelReponse:
    s = donnees["sommaire"]
    return SommaireMensuelReponse(
        mois=mois,
        mois_nom=NOMS_MOIS[mois - 1],
        revenu_brut=s["revenu_brut"],
        tps_percue=s["tps_percue"],
        tvq_percue=s["tvq_percue"],
        depenses_totales=s["depenses_totales"],
        tps_payee=s["tps_payee"],
        tvq_payee=s["tvq_payee"],
        tps_a_remettre=s["tps_a_remettre"],
        tvq_a_remettre=s["tvq_a_remettre"],
        depenses_admissibles_proratees=s["depenses_admissibles_proratees"],
    )


def _total_annuel(mois_liste: list[SommaireMensuelReponse]) -> SommaireMensuelReponse:
    champs = [
        "revenu_brut", "tps_percue", "tvq_percue", "depenses_totales",
        "tps_payee", "tvq_payee", "tps_a_remettre", "tvq_a_remettre", "depenses_admissibles_proratees",
    ]
    total = {champ: sum((getattr(m, champ) for m in mois_liste), Decimal("0")) for champ in champs}
    return SommaireMensuelReponse(mois=0, mois_nom="Total annuel", **total)


@routeur.get("/api/sommaire/{annee}", response_model=SommaireAnnuelReponse)
def sommaire_annuel(annee: int, session: Session = Depends(obtenir_session)):
    mois_liste = []
    for mois in range(1, 13):
        donnees = obtenir_donnees_periode(session, annee, mois)
        mois_liste.append(_sommaire_mensuel(mois, donnees))
    return SommaireAnnuelReponse(annee=annee, mois=mois_liste, total=_total_annuel(mois_liste))


@routeur.get("/api/tableau-de-bord", response_model=TableauDeBordReponse)
def tableau_de_bord(session: Session = Depends(obtenir_session)):
    aujourd_hui = date.today()
    donnees = obtenir_donnees_periode(session, aujourd_hui.year, aujourd_hui.month)
    sommaire = _sommaire_mensuel(aujourd_hui.month, donnees)
    alertes: list[AlerteReponse] = []

    if not donnees["revenus"]:
        alertes.append(AlerteReponse(type="revenus", message="Aucun revenu saisi pour le mois en cours"))
    if not donnees["kilometrage"]["entrees"]:
        alertes.append(AlerteReponse(type="kilometrage", message="Aucun kilométrage saisi pour le mois en cours"))
    if sommaire.tps_a_remettre > Decimal("100"):
        alertes.append(AlerteReponse(
            type="taxes",
            message=f"TPS à remettre élevée : {sommaire.tps_a_remettre:.2f} $",
        ))

    recurrentes_actives = session.query(DepenseRecurrente).filter_by(actif=True).count()
    depenses_recurrentes = sum(1 for d in donnees["depenses"] if d["est_recurrente"])
    if recurrentes_actives > depenses_recurrentes:
        alertes.append(AlerteReponse(
            type="recurrentes",
            message="Des dépenses récurrentes n'ont pas encore été générées pour ce mois",
        ))

    return TableauDeBordReponse(
        periode=PeriodeReponse(
            id=donnees["periode"]["id"],
            annee=aujourd_hui.year,
            mois=aujourd_hui.month,
            est_passee=est_periode_passee(aujourd_hui.year, aujourd_hui.month),
        ),
        sommaire=sommaire,
        alertes=alertes,
    )


@routeur.get("/api/export/excel/{annee}/{mois}")
def export_excel(annee: int, mois: int, session: Session = Depends(obtenir_session)):
    donnees = obtenir_donnees_periode(session, annee, mois)
    buffer = exporter_mois_excel(annee, mois, donnees)
    nom = f"comptabilite_{annee}_{mois:02d}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nom}"'},
    )


@routeur.get("/api/export/pdf/{annee}")
def export_pdf(annee: int, session: Session = Depends(obtenir_session)):
    sommaire = sommaire_annuel(annee, session)
    details = [obtenir_donnees_periode(session, annee, m) for m in range(1, 13)]
    buffer = exporter_annee_pdf(annee, sommaire.model_dump(), details)
    nom = f"rapport_comptable_{annee}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nom}"'},
    )
