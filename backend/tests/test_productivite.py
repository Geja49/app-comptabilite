from datetime import date
from decimal import Decimal

from app.services.calculs import arrondir
from app.routeurs.rapports import HEURES_TRAVAIL_PAR_JOUR, _productivite_depuis_donnees


def test_productivite_12h():
    donnees = {
        "revenus": [
            {"date": date(2026, 7, 1), "nombre_courses": 12, "revenu_brut": Decimal("300")},
            {"date": date(2026, 7, 2), "nombre_courses": 8, "revenu_brut": Decimal("200")},
        ],
        "sommaire": {
            "revenu_brut": Decimal("500"),
            "depenses_totales": Decimal("200"),
        },
    }
    prod = _productivite_depuis_donnees(donnees)
    assert prod.heures_par_jour == HEURES_TRAVAIL_PAR_JOUR
    assert prod.jours_travailles == 2
    assert prod.heures_totales == Decimal("24")
    assert prod.courses == 20
    assert prod.benefice == Decimal("300")
    assert prod.revenu_par_heure == arrondir(Decimal("500") / Decimal("24"))
    assert prod.marge_benefice == arrondir(Decimal("300") / Decimal("500"))
