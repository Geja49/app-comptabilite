from decimal import Decimal

from app.modeles.parametres_fiscaux import MethodeTpsTvq
from app.services import calculs, impots


def test_sommaire_reguliere_identique_calculs():
    revenus = [calculs.calculer_revenu(62, Decimal("985.58"), Decimal("72.90"))]
    depenses = [calculs.calculer_taxes_depuis_ht(Decimal("320"))]
    depenses_fmt = [
        {
            "montant_ht": d["montant_ht"],
            "tps": d["tps"],
            "tvq": d["tvq"],
            "montant_total": d["montant_total"],
        }
        for d in depenses
    ]
    via_calculs = calculs.calculer_sommaire_mensuel(revenus, depenses_fmt, Decimal("0.72"))
    via_impots = impots.calculer_sommaire_mensuel(
        revenus, depenses_fmt, Decimal("0.72"), methode=MethodeTpsTvq.REGULIERE
    )
    assert via_impots["depenses_admissibles_proratees"] == Decimal("230.40")
    assert via_impots["tps_a_remettre"] == via_calculs["tps_a_remettre"]
    assert via_impots["tvq_a_remettre"] == via_calculs["tvq_a_remettre"]
    assert via_impots["methode_tps_tvq"] == MethodeTpsTvq.REGULIERE


def test_sommaire_reguliere_redevance_et_ttc():
    revenus = [calculs.calculer_revenu(22, Decimal("312.01"), Decimal("19"))]
    depenses: list[dict] = []
    sommaire = impots.calculer_sommaire_mensuel(
        revenus, depenses, Decimal("0"), methode=MethodeTpsTvq.REGULIERE
    )
    assert sommaire["redevance_totale"] == Decimal("19.80")
    assert sommaire["revenu_total_ttc"] == Decimal("358.73")
    assert sommaire["tps_a_remettre"] == Decimal("15.60")
    assert sommaire["tvq_a_remettre"] == Decimal("31.12")
