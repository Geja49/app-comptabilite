from decimal import Decimal

from app.services import calculs


def test_calculer_revenu_courses_simples():
    resultat = calculs.calculer_revenu(22, Decimal("312.01"), Decimal("19"))
    assert resultat["redevance_simple"] == Decimal("19.80")
    assert resultat["redevance_bus"] == Decimal("0.00")
    assert resultat["redevance_gouv"] == Decimal("19.80")
    assert resultat["total_net_encaisse"] == Decimal("397.53")


def test_calculer_revenu_mixte():
    resultat = calculs.calculer_revenu(10, Decimal("200.00"), Decimal("5"), nombre_redevances=8)
    assert resultat["redevance_simple"] == Decimal("9.00")
    assert resultat["redevance_bus"] == Decimal("7.20")
    assert resultat["redevance_gouv"] == Decimal("16.20")
    assert resultat["total_net_encaisse"] == Decimal("243.95")


def test_calculer_revenu_bus_seulement():
    resultat = calculs.calculer_revenu(0, Decimal("312.01"), Decimal("19"), nombre_redevances=20)
    assert resultat["redevance_simple"] == Decimal("0.00")
    assert resultat["redevance_bus"] == Decimal("18.00")
    assert resultat["redevance_gouv"] == Decimal("18.00")
    assert resultat["total_net_encaisse"] == Decimal("357.93")
