from decimal import Decimal
from typing import Any

from app.modeles.parametres_fiscaux import MethodeTpsTvq
from app.services.calculs import arrondir

ZERO = Decimal("0")


def _taux(valeur: Any) -> Decimal:
    return Decimal(str(valeur))


def calculer_base_rapide(revenus: list[dict]) -> Decimal:
    """Revenu total taxes incluses, hors pourboires."""
    base = sum(
        (r["revenu_brut"] + r["tps_percue"] + r["tvq_percue"] for r in revenus),
        ZERO,
    )
    return arrondir(base)


def calculer_sommaire_mensuel(
    revenus: list[dict],
    depenses: list[dict],
    taux_pro: Decimal,
    methode: str = MethodeTpsTvq.REGULIERE,
    tps_taux_rapide: Decimal = Decimal("0.036"),
    tvq_taux_rapide: Decimal = Decimal("0.066"),
) -> dict:
    revenu_brut = sum((r["revenu_brut"] for r in revenus), ZERO)
    tps_percue = sum((r["tps_percue"] for r in revenus), ZERO)
    tvq_percue = sum((r["tvq_percue"] for r in revenus), ZERO)
    redevance_totale = sum((r.get("redevance_gouv", ZERO) for r in revenus), ZERO)
    depenses_totales = sum((d["montant_total"] for d in depenses), ZERO)
    depenses_ht = sum((d["montant_ht"] for d in depenses), ZERO)
    tps_payee = sum((d["tps"] for d in depenses), ZERO)
    tvq_payee = sum((d["tvq"] for d in depenses), ZERO)
    depenses_admissibles = arrondir(depenses_ht * taux_pro)
    revenu_total_ttc = calculer_base_rapide(revenus)

    if methode == MethodeTpsTvq.RAPIDE:
        tps_a_remettre = arrondir(revenu_total_ttc * _taux(tps_taux_rapide))
        tvq_a_remettre = arrondir(revenu_total_ttc * _taux(tvq_taux_rapide))
    else:
        tps_a_remettre = arrondir(tps_percue - tps_payee)
        tvq_a_remettre = arrondir(tvq_percue - tvq_payee)

    return {
        "revenu_brut": arrondir(revenu_brut),
        "tps_percue": arrondir(tps_percue),
        "tvq_percue": arrondir(tvq_percue),
        "depenses_totales": arrondir(depenses_totales),
        "tps_payee": arrondir(tps_payee),
        "tvq_payee": arrondir(tvq_payee),
        "tps_a_remettre": tps_a_remettre,
        "tvq_a_remettre": tvq_a_remettre,
        "depenses_admissibles_proratees": depenses_admissibles,
        "taux_pro": taux_pro,
        "methode_tps_tvq": methode,
        "redevance_totale": arrondir(redevance_totale),
        "revenu_total_ttc": revenu_total_ttc,
        "rabais_rapide_applique": ZERO,
    }


def appliquer_rabais_annuel_rapide(
    sommaires_mensuels: list[dict],
    rabais_taux: Decimal = Decimal("0.01"),
    rabais_plafond: Decimal = Decimal("30000"),
) -> tuple[list[dict], Decimal]:
    """Applique le rabais de 1 % sur les premiers 30 000 $ de base annuelle.

    Le rabais est réparti chronologiquement sur les mois et réduit d'abord
    la TPS à remettre, puis la TVQ si nécessaire.
    """
    plafond_restant = _taux(rabais_plafond)
    taux = _taux(rabais_taux)
    total_rabais = ZERO
    resultats: list[dict] = []

    for sommaire in sommaires_mensuels:
        copie = dict(sommaire)
        base_mois = copie.get("revenu_total_ttc", ZERO)
        base_eligible = min(base_mois, plafond_restant)
        rabais_mois = arrondir(base_eligible * taux) if base_eligible > 0 else ZERO
        plafond_restant = arrondir(plafond_restant - base_eligible)

        tps = copie["tps_a_remettre"]
        tvq = copie["tvq_a_remettre"]
        reduction_tps = min(tps, rabais_mois)
        reste = arrondir(rabais_mois - reduction_tps)
        reduction_tvq = min(tvq, reste)

        copie["tps_a_remettre"] = arrondir(tps - reduction_tps)
        copie["tvq_a_remettre"] = arrondir(tvq - reduction_tvq)
        copie["rabais_rapide_applique"] = arrondir(reduction_tps + reduction_tvq)
        total_rabais = arrondir(total_rabais + copie["rabais_rapide_applique"])
        resultats.append(copie)

    return resultats, total_rabais
