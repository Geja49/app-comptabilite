from decimal import Decimal

from app.services import calculs


def test_calculer_revenu():
    resultat = calculs.calculer_revenu(22, Decimal("312.01"), Decimal("19"))
    assert resultat["redevance_gouv"] == Decimal("19.80")
    assert resultat["tps_percue"] == Decimal("15.60")
    assert resultat["tvq_percue"] == Decimal("31.12")
    assert resultat["total_net_encaisse"] == Decimal("397.53")


def test_calculer_taxes_depuis_ht():
    resultat = calculs.calculer_taxes_depuis_ht(Decimal("50"))
    assert resultat["montant_ht"] == Decimal("50.00")
    assert resultat["tps"] == Decimal("2.50")
    assert resultat["tvq"] == Decimal("4.99")
    assert resultat["montant_total"] == Decimal("57.49")


def test_calculer_taxes_depuis_ttc():
    resultat = calculs.calculer_taxes_depuis_ttc(Decimal("57.49"))
    assert resultat["montant_ht"] == Decimal("50.00")


def test_calculer_kilometrage():
    resultat = calculs.calculer_kilometrage_jour(Decimal("120000"), Decimal("120250"), Decimal("180"))
    assert resultat["km_totaux"] == Decimal("250.0")
    assert resultat["taux_pro"] == Decimal("0.7200")


def test_sommaire_mensuel():
    revenus = [calculs.calculer_revenu(62, Decimal("985.58"), Decimal("72.90"))]
    depenses = [calculs.calculer_taxes_depuis_ht(Decimal("320"))]
    depenses_fmt = [{"montant_ht": d["montant_ht"], "tps": d["tps"], "tvq": d["tvq"], "montant_total": d["montant_total"]} for d in depenses]
    sommaire = calculs.calculer_sommaire_mensuel(revenus, depenses_fmt, Decimal("0.72"))
    assert sommaire["depenses_admissibles_proratees"] == Decimal("230.40")
