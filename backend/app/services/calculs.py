from decimal import Decimal, ROUND_HALF_UP

TPS_TAUX = Decimal("0.05")
TVQ_TAUX = Decimal("0.09975")
TTC_FACTEUR = Decimal("1.14975")
REDEVANCE_PAR_COURSE = Decimal("0.90")
DEUX_DECIMALES = Decimal("0.01")
QUATRE_DECIMALES = Decimal("0.0001")


def arrondir(montant: Decimal, decimales: Decimal = DEUX_DECIMALES) -> Decimal:
    return montant.quantize(decimales, rounding=ROUND_HALF_UP)


def calculer_taxes_depuis_ht(montant_ht: Decimal) -> dict[str, Decimal]:
    montant_ht = arrondir(montant_ht)
    tps = arrondir(montant_ht * TPS_TAUX)
    tvq = arrondir(montant_ht * TVQ_TAUX)
    total = arrondir(montant_ht + tps + tvq)
    return {"montant_ht": montant_ht, "tps": tps, "tvq": tvq, "montant_total": total}


def calculer_taxes_depuis_ttc(montant_ttc: Decimal) -> dict[str, Decimal]:
    montant_ttc = arrondir(montant_ttc)
    montant_ht = arrondir(montant_ttc / TTC_FACTEUR)
    tps = arrondir(montant_ht * TPS_TAUX)
    tvq = arrondir(montant_ht * TVQ_TAUX)
    total = arrondir(montant_ht + tps + tvq)
    return {"montant_ht": montant_ht, "tps": tps, "tvq": tvq, "montant_total": total}


def calculer_revenu(nombre_courses: int, revenu_brut: Decimal, pourboires: Decimal) -> dict[str, Decimal | int]:
    revenu_brut = arrondir(revenu_brut)
    pourboires = arrondir(pourboires)
    redevance = arrondir(Decimal(nombre_courses) * REDEVANCE_PAR_COURSE)
    tps = arrondir(revenu_brut * TPS_TAUX)
    tvq = arrondir(revenu_brut * TVQ_TAUX)
    total_net = arrondir(revenu_brut + redevance + tps + tvq + pourboires)
    return {
        "nombre_courses": nombre_courses,
        "revenu_brut": revenu_brut,
        "pourboires": pourboires,
        "redevance_gouv": redevance,
        "tps_percue": tps,
        "tvq_percue": tvq,
        "total_net_encaisse": total_net,
    }


def calculer_kilometrage_jour(odometre_debut: Decimal, odometre_fin: Decimal, km_professionnels: Decimal) -> dict[str, Decimal]:
    km_totaux = arrondir(odometre_fin - odometre_debut, Decimal("0.1"))
    km_pro = arrondir(km_professionnels, Decimal("0.1"))
    taux = arrondir(km_pro / km_totaux, QUATRE_DECIMALES) if km_totaux > 0 else Decimal("0")
    return {"km_totaux": km_totaux, "km_professionnels": km_pro, "taux_pro": taux}


def agreger_kilometrage(entrees: list[dict]) -> dict[str, Decimal]:
    km_totaux = sum((e["km_totaux"] for e in entrees), Decimal("0"))
    km_pro = sum((e["km_professionnels"] for e in entrees), Decimal("0"))
    km_totaux = arrondir(km_totaux, Decimal("0.1"))
    km_pro = arrondir(km_pro, Decimal("0.1"))
    taux = arrondir(km_pro / km_totaux, QUATRE_DECIMALES) if km_totaux > 0 else Decimal("0")
    return {"km_totaux_mois": km_totaux, "km_pro_mois": km_pro, "taux_pro": taux}


def calculer_sommaire_mensuel(
    revenus: list[dict],
    depenses: list[dict],
    taux_pro: Decimal,
) -> dict:
    """Conserve la compatibilité : sommaire selon la méthode régulière."""
    from app.modeles.parametres_fiscaux import MethodeTpsTvq
    from app.services import impots

    return impots.calculer_sommaire_mensuel(
        revenus, depenses, taux_pro, methode=MethodeTpsTvq.REGULIERE
    )
