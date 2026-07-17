from decimal import Decimal

from app.modeles.parametres_fiscaux import MethodeTpsTvq
from app.services import calculs, impots


def test_methode_rapide_10000_ttc():
    """Revenu total TTC de 10 000 $ → TPS 360 $, TVQ 660 $."""
    # Base rapide = revenu_brut + tps + tvq (hors pourboires)
    # Pour obtenir exactement 10000 TTC : brut X + 5%X + 9.975%X = 10000
    # X * 1.14975 = 10000 → X = 8697.54 (après arrondi unitaire)
    revenu = calculs.calculer_revenu(0, Decimal("8697.54"), Decimal("0"))
    base = revenu["revenu_brut"] + revenu["tps_percue"] + revenu["tvq_percue"]
    # Ajustement via base calculée directement si l'arrondi le déplace
    revenus = [revenu]
    depenses: list[dict] = []
    sommaire = impots.calculer_sommaire_mensuel(
        revenus, depenses, Decimal("0"), methode=MethodeTpsTvq.RAPIDE
    )
    base_calculee = sommaire["revenu_total_ttc"]
    assert sommaire["tps_a_remettre"] == calculs.arrondir(base_calculee * Decimal("0.036"))
    assert sommaire["tvq_a_remettre"] == calculs.arrondir(base_calculee * Decimal("0.066"))
    # Cas nominal exact demandé : base forcée à 10000
    revenus_forces = [{
        "revenu_brut": Decimal("8700.00"),
        "tps_percue": Decimal("800.00"),
        "tvq_percue": Decimal("500.00"),
        "redevance_gouv": Decimal("0"),
        "pourboires": Decimal("0"),
    }]
    # 8700+800+500 = 10000
    sommaire_exact = impots.calculer_sommaire_mensuel(
        revenus_forces, depenses, Decimal("0"), methode=MethodeTpsTvq.RAPIDE
    )
    assert sommaire_exact["revenu_total_ttc"] == Decimal("10000.00")
    assert sommaire_exact["tps_a_remettre"] == Decimal("360.00")
    assert sommaire_exact["tvq_a_remettre"] == Decimal("660.00")
    # Les taxes payées sur dépenses ne réduisent pas le montant à remettre
    depenses_avec_taxes = [{
        "montant_ht": Decimal("200"),
        "tps": Decimal("10"),
        "tvq": Decimal("20"),
        "montant_total": Decimal("230"),
    }]
    sommaire_sans_credit = impots.calculer_sommaire_mensuel(
        revenus_forces, depenses_avec_taxes, Decimal("0"), methode=MethodeTpsTvq.RAPIDE
    )
    assert sommaire_sans_credit["tps_a_remettre"] == Decimal("360.00")
    assert sommaire_sans_credit["tvq_a_remettre"] == Decimal("660.00")
    assert sommaire_sans_credit["tps_payee"] == Decimal("10.00")


def test_pourboires_exclus_de_la_base_rapide():
    revenus = [calculs.calculer_revenu(10, Decimal("100"), Decimal("50"))]
    sommaire = impots.calculer_sommaire_mensuel(
        revenus, [], Decimal("0"), methode=MethodeTpsTvq.RAPIDE
    )
    # 100 + 5 + 9.98 = 114.98 (tvq arrondie)
    assert sommaire["revenu_total_ttc"] == Decimal("114.98")


def test_rabais_rapide_sur_30000_reparti():
    mois = []
    for i in range(3):
        mois.append({
            "revenu_brut": Decimal("10000"),
            "tps_percue": Decimal("0"),
            "tvq_percue": Decimal("0"),
            "depenses_totales": Decimal("0"),
            "tps_payee": Decimal("0"),
            "tvq_payee": Decimal("0"),
            "tps_a_remettre": Decimal("360.00"),
            "tvq_a_remettre": Decimal("660.00"),
            "depenses_admissibles_proratees": Decimal("0"),
            "revenu_total_ttc": Decimal("10000.00"),
            "redevance_totale": Decimal("0"),
            "methode_tps_tvq": MethodeTpsTvq.RAPIDE,
            "rabais_rapide_applique": Decimal("0"),
        })
    # 3 × 10000 = 30000 → rabais total = 300 $
    # Mois 4 dépasse le plafond
    mois.append({
        "revenu_brut": Decimal("5000"),
        "tps_percue": Decimal("0"),
        "tvq_percue": Decimal("0"),
        "depenses_totales": Decimal("0"),
        "tps_payee": Decimal("0"),
        "tvq_payee": Decimal("0"),
        "tps_a_remettre": Decimal("180.00"),
        "tvq_a_remettre": Decimal("330.00"),
        "depenses_admissibles_proratees": Decimal("0"),
        "revenu_total_ttc": Decimal("5000.00"),
        "redevance_totale": Decimal("0"),
        "methode_tps_tvq": MethodeTpsTvq.RAPIDE,
        "rabais_rapide_applique": Decimal("0"),
    })

    resultats, total_rabais = impots.appliquer_rabais_annuel_rapide(mois)
    assert total_rabais == Decimal("300.00")
    assert resultats[0]["rabais_rapide_applique"] == Decimal("100.00")
    assert resultats[1]["rabais_rapide_applique"] == Decimal("100.00")
    assert resultats[2]["rabais_rapide_applique"] == Decimal("100.00")
    assert resultats[3]["rabais_rapide_applique"] == Decimal("0.00")
    # Rabais réduit d'abord la TPS
    assert resultats[0]["tps_a_remettre"] == Decimal("260.00")
    assert resultats[0]["tvq_a_remettre"] == Decimal("660.00")
