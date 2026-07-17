from datetime import date
from decimal import Decimal

from app.modeles import Depense, DepenseRecurrente, FrequenceDepenseRecurrente, Periode, Revenu
from app.services.periode_service import generer_depenses_recurrentes


def test_location_par_jour_travail(client=None):
    """Test unitaire sans API : 2 jours de revenu → 2 dépenses de 110 $."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.database import Base
    from app.modeles import CategorieDepense

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    categorie = CategorieDepense(nom="Location véhicule", est_systeme=True)
    session.add(categorie)
    session.flush()

    periode = Periode(annee=2026, mois=7)
    session.add(periode)
    session.flush()

    recurrente = DepenseRecurrente(
        fournisseur="Location véhicule",
        categorie_id=categorie.id,
        montant=Decimal("110.00"),
        montant_ttc=True,
        jour_du_mois=1,
        frequence=FrequenceDepenseRecurrente.PAR_JOUR_TRAVAIL,
        actif=True,
    )
    session.add(recurrente)
    session.add(Revenu(periode_id=periode.id, date=date(2026, 7, 1), nombre_courses=10, revenu_brut=Decimal("200"), pourboires=Decimal("0")))
    session.add(Revenu(periode_id=periode.id, date=date(2026, 7, 3), nombre_courses=8, revenu_brut=Decimal("150"), pourboires=Decimal("0")))
    session.commit()

    session.refresh(periode)
    creees = generer_depenses_recurrentes(session, periode)
    assert len(creees) == 2
    assert all(d.montant_saisi == Decimal("110.00") for d in creees)
    assert {d.date for d in creees} == {date(2026, 7, 1), date(2026, 7, 3)}

    # Idempotent : pas de doublon
    encore = generer_depenses_recurrentes(session, periode)
    assert encore == []
    assert session.query(Depense).count() == 2
