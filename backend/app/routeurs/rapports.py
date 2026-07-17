from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.modeles import DepenseRecurrente, MethodeTpsTvq
from app.schemas import (
    AlerteReponse,
    PeriodeReponse,
    SommaireAnnuelReponse,
    SommaireMensuelReponse,
    TableauDeBordReponse,
)
from app.services.export_excel import NOMS_MOIS, exporter_mois_excel
from app.services.export_pdf import exporter_annee_pdf
from app.services.impots import appliquer_rabais_annuel_rapide
from app.services.parametres_fiscaux_service import obtenir_ou_creer_parametres_fiscaux
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
        methode_tps_tvq=s.get("methode_tps_tvq", MethodeTpsTvq.REGULIERE),
        redevance_totale=s.get("redevance_totale", Decimal("0")),
        revenu_total_ttc=s.get("revenu_total_ttc", Decimal("0")),
        rabais_rapide_applique=s.get("rabais_rapide_applique", Decimal("0")),
    )


def _total_annuel(
    mois_liste: list[SommaireMensuelReponse],
    methode: str,
    rabais_total: Decimal = Decimal("0"),
) -> SommaireMensuelReponse:
    champs = [
        "revenu_brut", "tps_percue", "tvq_percue", "depenses_totales",
        "tps_payee", "tvq_payee", "tps_a_remettre", "tvq_a_remettre",
        "depenses_admissibles_proratees", "redevance_totale", "revenu_total_ttc",
        "rabais_rapide_applique",
    ]
    total = {champ: sum((getattr(m, champ) for m in mois_liste), Decimal("0")) for champ in champs}
    return SommaireMensuelReponse(
        mois=0,
        mois_nom="Total annuel",
        methode_tps_tvq=methode,
        **total,
    )


@routeur.get("/api/sommaire/{annee}", response_model=SommaireAnnuelReponse)
def sommaire_annuel(annee: int, session: Session = Depends(obtenir_session)):
    parametres = obtenir_ou_creer_parametres_fiscaux(session, annee)
    mois_bruts: list[dict] = []
    for mois in range(1, 13):
        donnees = obtenir_donnees_periode(session, annee, mois)
        mois_bruts.append({**donnees["sommaire"], "mois": mois})

    rabais_total = Decimal("0")
    if parametres.methode_tps_tvq == MethodeTpsTvq.RAPIDE:
        mois_bruts, rabais_total = appliquer_rabais_annuel_rapide(
            mois_bruts,
            rabais_taux=parametres.rabais_rapide_taux,
            rabais_plafond=parametres.rabais_rapide_plafond,
        )

    mois_liste = []
    for brut in mois_bruts:
        mois = brut["mois"]
        mois_liste.append(SommaireMensuelReponse(
            mois=mois,
            mois_nom=NOMS_MOIS[mois - 1],
            revenu_brut=brut["revenu_brut"],
            tps_percue=brut["tps_percue"],
            tvq_percue=brut["tvq_percue"],
            depenses_totales=brut["depenses_totales"],
            tps_payee=brut["tps_payee"],
            tvq_payee=brut["tvq_payee"],
            tps_a_remettre=brut["tps_a_remettre"],
            tvq_a_remettre=brut["tvq_a_remettre"],
            depenses_admissibles_proratees=brut["depenses_admissibles_proratees"],
            methode_tps_tvq=brut.get("methode_tps_tvq", parametres.methode_tps_tvq),
            redevance_totale=brut.get("redevance_totale", Decimal("0")),
            revenu_total_ttc=brut.get("revenu_total_ttc", Decimal("0")),
            rabais_rapide_applique=brut.get("rabais_rapide_applique", Decimal("0")),
        ))

    return SommaireAnnuelReponse(
        annee=annee,
        mois=mois_liste,
        total=_total_annuel(mois_liste, parametres.methode_tps_tvq, rabais_total),
        methode_tps_tvq=parametres.methode_tps_tvq,
        rabais_rapide_applique=rabais_total,
    )


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

    from app.modeles import FrequenceDepenseRecurrente
    from app.pagination import LIMITE_MAX

    recurrentes_actives = (
        session.query(DepenseRecurrente)
        .filter_by(actif=True)
        .limit(LIMITE_MAX)
        .all()
    )
    dates_revenus = {r["date"] for r in donnees["revenus"]}
    depenses_par_recurrente = {}
    for d in donnees["depenses"]:
        if d["depense_recurrente_id"] is None:
            continue
        depenses_par_recurrente.setdefault(d["depense_recurrente_id"], set()).add(d["date"])

    manquantes = False
    for recurrente in recurrentes_actives:
        dates_existantes = depenses_par_recurrente.get(recurrente.id, set())
        if recurrente.frequence == FrequenceDepenseRecurrente.PAR_JOUR_TRAVAIL:
            if dates_revenus - dates_existantes:
                manquantes = True
                break
        elif not dates_existantes:
            manquantes = True
            break

    if manquantes:
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
