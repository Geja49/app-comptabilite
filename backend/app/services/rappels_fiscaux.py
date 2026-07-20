"""Calendrier fiscal Québec / Canada pour chauffeurs de taxi (rappels).

Sources (règles générales Revenu Québec / ARC) :
- TPS/TVQ mensuelle ou trimestrielle : déclaration et paiement ≈ 1 mois après la fin
  de la période.
- TPS/TVQ annuelle (particulier, exercice 31 déc.) : paiement au 30 avril,
  déclaration au 15 juin.
- Impôt sur le revenu (travailleur autonome) : paiement au 30 avril,
  déclaration au 15 juin.
- Acomptes d'impôt : 15 mars, 15 juin, 15 septembre, 15 décembre.
- Redevance transport (0,90 $/course) : remise avec la déclaration de taxes.

Ces dates sont indicatives ; les calendriers officiels peuvent reporter un jour
ouvrable si l'échéance tombe un week-end ou un jour férié.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from enum import StrEnum

NOMS_MOIS = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


class FrequenceDeclaration(StrEnum):
    MENSUELLE = "mensuelle"
    TRIMESTRIELLE = "trimestrielle"
    ANNUELLE = "annuelle"


JOURS_FENETRE = 90  # rappels passés récents + à venir


def _dernier_jour_mois(annee: int, mois: int) -> date:
    return date(annee, mois, monthrange(annee, mois)[1])


def _ajouter_mois(jour: date, mois: int) -> date:
    total = jour.month - 1 + mois
    annee = jour.year + total // 12
    mois_cible = total % 12 + 1
    jour_max = monthrange(annee, mois_cible)[1]
    return date(annee, mois_cible, min(jour.day, jour_max))


def _fin_mois_suivant(fin_periode: date) -> date:
    """Date limite typique : dernier jour du mois suivant la fin de période."""
    suivant = _ajouter_mois(date(fin_periode.year, fin_periode.month, 1), 1)
    return _dernier_jour_mois(suivant.year, suivant.month)


def _urgence(jours_restants: int) -> str:
    if jours_restants < 0:
        return "echue"
    if jours_restants <= 14:
        return "haute"
    if jours_restants <= 30:
        return "moyenne"
    return "basse"


def _rappel(
    *,
    impot: str,
    type_rappel: str,
    titre: str,
    description: str,
    date_limite: date,
    organisme: str,
    periode: str,
    aujourd_hui: date,
) -> dict:
    jours = (date_limite - aujourd_hui).days
    return {
        "impot": impot,
        "type": type_rappel,
        "titre": titre,
        "description": description,
        "date_limite": date_limite.isoformat(),
        "jours_restants": jours,
        "urgence": _urgence(jours),
        "organisme": organisme,
        "periode": periode,
    }


def _periodes_tps_tvq(frequence: str, annee_ref: int) -> list[tuple[str, date, date]]:
    """Retourne (libellé période, début, fin) pour l'année de référence ±1."""
    resultats: list[tuple[str, date, date]] = []
    if frequence == FrequenceDeclaration.MENSUELLE:
        for annee in (annee_ref - 1, annee_ref, annee_ref + 1):
            for mois in range(1, 13):
                debut = date(annee, mois, 1)
                fin = _dernier_jour_mois(annee, mois)
                resultats.append((f"{NOMS_MOIS[mois - 1]} {annee}", debut, fin))
    elif frequence == FrequenceDeclaration.TRIMESTRIELLE:
        trimestres = (
            (1, 3, "1er trimestre"),
            (4, 6, "2e trimestre"),
            (7, 9, "3e trimestre"),
            (10, 12, "4e trimestre"),
        )
        for annee in (annee_ref - 1, annee_ref, annee_ref + 1):
            for mois_debut, mois_fin, nom in trimestres:
                debut = date(annee, mois_debut, 1)
                fin = _dernier_jour_mois(annee, mois_fin)
                resultats.append((f"{nom} {annee}", debut, fin))
    else:
        for annee in (annee_ref - 1, annee_ref, annee_ref + 1):
            debut = date(annee, 1, 1)
            fin = date(annee, 12, 31)
            resultats.append((f"Exercice {annee}", debut, fin))
    return resultats


def _rappels_tps_tvq(frequence: str, aujourd_hui: date) -> list[dict]:
    rappels: list[dict] = []
    for periode_libelle, _debut, fin in _periodes_tps_tvq(frequence, aujourd_hui.year):
        if frequence == FrequenceDeclaration.ANNUELLE:
            # Particulier travailleur autonome, exercice 31 déc. (cas taxi typique)
            date_paiement = date(fin.year + 1, 4, 30)
            date_declaration = date(fin.year + 1, 6, 15)
            rappels.append(
                _rappel(
                    impot="tps_tvq",
                    type_rappel="paiement",
                    titre="Paiement TPS / TVQ",
                    description=(
                        f"Remettre la TPS et la TVQ nettes pour {periode_libelle} "
                        "(particulier, exercice au 31 décembre)."
                    ),
                    date_limite=date_paiement,
                    organisme="Revenu Québec",
                    periode=periode_libelle,
                    aujourd_hui=aujourd_hui,
                )
            )
            rappels.append(
                _rappel(
                    impot="tps_tvq",
                    type_rappel="declaration",
                    titre="Déclaration TPS / TVQ",
                    description=(
                        f"Produire les déclarations de TPS et de TVQ pour {periode_libelle} "
                        "(même si un répondant a déjà versé une partie des taxes)."
                    ),
                    date_limite=date_declaration,
                    organisme="Revenu Québec",
                    periode=periode_libelle,
                    aujourd_hui=aujourd_hui,
                )
            )
            rappels.append(
                _rappel(
                    impot="redevance",
                    type_rappel="paiement",
                    titre="Redevance transport (0,90 $/course)",
                    description=(
                        f"Déclarer et verser la redevance perçue avec vos taxes pour {periode_libelle}."
                    ),
                    date_limite=date_paiement,
                    organisme="Revenu Québec",
                    periode=periode_libelle,
                    aujourd_hui=aujourd_hui,
                )
            )
        else:
            echeance = _fin_mois_suivant(fin)
            rappels.append(
                _rappel(
                    impot="tps_tvq",
                    type_rappel="declaration",
                    titre="Déclaration et paiement TPS / TVQ",
                    description=(
                        f"Produire la déclaration et payer le solde pour {periode_libelle} "
                        "(fréquence {frequence})."
                    ),
                    date_limite=echeance,
                    organisme="Revenu Québec",
                    periode=periode_libelle,
                    aujourd_hui=aujourd_hui,
                )
            )
            rappels.append(
                _rappel(
                    impot="redevance",
                    type_rappel="paiement",
                    titre="Redevance transport (0,90 $/course)",
                    description=(
                        f"Inclure la redevance perçue dans la déclaration de taxes ({periode_libelle})."
                    ),
                    date_limite=echeance,
                    organisme="Revenu Québec",
                    periode=periode_libelle,
                    aujourd_hui=aujourd_hui,
                )
            )
    return rappels


def _rappels_impot_revenu(aujourd_hui: date) -> list[dict]:
    rappels: list[dict] = []
    for annee in (aujourd_hui.year - 1, aujourd_hui.year):
        periode = f"Année d'imposition {annee}"
        rappels.append(
            _rappel(
                impot="impot_revenu",
                type_rappel="paiement",
                titre="Paiement d'impôt sur le revenu",
                description=(
                    "Travailleur autonome : solde d'impôt fédéral et québécois à payer "
                    f"pour {periode}."
                ),
                date_limite=date(annee + 1, 4, 30),
                organisme="ARC et Revenu Québec",
                periode=periode,
                aujourd_hui=aujourd_hui,
            )
        )
        rappels.append(
            _rappel(
                impot="impot_revenu",
                type_rappel="declaration",
                titre="Déclarations de revenus",
                description=(
                    "Produire T1 (fédéral) et TP-1 (Québec) — délai prolongé au 15 juin "
                    "pour les particuliers avec revenu d'entreprise."
                ),
                date_limite=date(annee + 1, 6, 15),
                organisme="ARC et Revenu Québec",
                periode=periode,
                aujourd_hui=aujourd_hui,
            )
        )
    return rappels


def _rappels_acomptes(aujourd_hui: date) -> list[dict]:
    rappels: list[dict] = []
    echeances = ((3, 15), (6, 15), (9, 15), (12, 15))
    for annee in (aujourd_hui.year - 1, aujourd_hui.year, aujourd_hui.year + 1):
        for mois, jour in echeances:
            rappels.append(
                _rappel(
                    impot="acomptes_impot",
                    type_rappel="paiement",
                    titre="Acompte provisionnel d'impôt",
                    description=(
                        "Versement trimestriel d'impôt estimé (fédéral / Québec), "
                        "si vous y êtes assujetti."
                    ),
                    date_limite=date(annee, mois, jour),
                    organisme="ARC et Revenu Québec",
                    periode=f"{annee}-{mois:02d}",
                    aujourd_hui=aujourd_hui,
                )
            )
    return rappels


def generer_rappels_fiscaux(
    frequence_declaration: str = FrequenceDeclaration.ANNUELLE.value,
    aujourd_hui: date | None = None,
    horizon_jours: int = JOURS_FENETRE,
) -> list[dict]:
    """Liste les rappels pertinents (échus récents + à venir dans l'horizon)."""
    jour = aujourd_hui or date.today()
    frequence = frequence_declaration or FrequenceDeclaration.ANNUELLE.value
    if frequence not in {f.value for f in FrequenceDeclaration}:
        frequence = FrequenceDeclaration.ANNUELLE.value

    tous = (
        _rappels_tps_tvq(frequence, jour)
        + _rappels_impot_revenu(jour)
        + _rappels_acomptes(jour)
    )

    filtrés: list[dict] = []
    for rappel in tous:
        limite = date.fromisoformat(rappel["date_limite"])
        if limite < jour - timedelta(days=14):
            continue
        if limite > jour + timedelta(days=horizon_jours):
            continue
        filtrés.append(rappel)

    filtrés.sort(key=lambda r: (r["date_limite"], r["impot"], r["type"]))
    return filtrés
