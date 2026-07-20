from datetime import date

from app.services.rappels_fiscaux import FrequenceDeclaration, generer_rappels_fiscaux


def test_rappels_annuels_particulier_en_mars():
    rappels = generer_rappels_fiscaux(
        frequence_declaration=FrequenceDeclaration.ANNUELLE,
        aujourd_hui=date(2026, 3, 15),
        horizon_jours=120,
    )
    titres = {r["titre"] for r in rappels}
    assert "Paiement TPS / TVQ" in titres
    assert "Déclaration TPS / TVQ" in titres
    assert "Paiement d'impôt sur le revenu" in titres
    assert "Déclarations de revenus" in titres
    assert any(r["impot"] == "redevance" for r in rappels)

    paiement_tps = next(r for r in rappels if r["titre"] == "Paiement TPS / TVQ" and r["periode"] == "Exercice 2025")
    assert paiement_tps["date_limite"] == "2026-04-30"
    declaration_tps = next(
        r for r in rappels if r["titre"] == "Déclaration TPS / TVQ" and r["periode"] == "Exercice 2025"
    )
    assert declaration_tps["date_limite"] == "2026-06-15"


def test_rappels_trimestriels_incluent_echeance_prochaine():
    rappels = generer_rappels_fiscaux(
        frequence_declaration=FrequenceDeclaration.TRIMESTRIELLE,
        aujourd_hui=date(2026, 4, 10),
        horizon_jours=60,
    )
    tps = [r for r in rappels if r["impot"] == "tps_tvq"]
    assert tps
    assert any(r["date_limite"] == "2026-04-30" for r in tps)


def test_acomptes_provisionnels_presents():
    rappels = generer_rappels_fiscaux(
        frequence_declaration=FrequenceDeclaration.ANNUELLE,
        aujourd_hui=date(2026, 6, 1),
        horizon_jours=30,
    )
    assert any(r["impot"] == "acomptes_impot" and r["date_limite"] == "2026-06-15" for r in rappels)
