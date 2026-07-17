from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, obtenir_session
from app.main import app
from app.modeles import MethodeTpsTvq


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def _session():
        session = SessionTest()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[obtenir_session] = _session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_parametres_cree_defaut(client):
    reponse = client.get("/api/parametres-fiscaux/2026")
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["annee"] == 2026
    assert data["methode_tps_tvq"] == MethodeTpsTvq.REGULIERE
    assert Decimal(data["tps_taux_rapide"]) == Decimal("0.036")
    assert Decimal(data["tvq_taux_rapide"]) == Decimal("0.066")
    assert Decimal(data["rabais_rapide_plafond"]) == Decimal("30000")


def test_put_change_methode(client):
    reponse = client.put(
        "/api/parametres-fiscaux/2026",
        json={"methode_tps_tvq": "rapide"},
    )
    assert reponse.status_code == 200
    assert reponse.json()["methode_tps_tvq"] == "rapide"

    relecture = client.get("/api/parametres-fiscaux/2026")
    assert relecture.json()["methode_tps_tvq"] == "rapide"


def test_put_methode_invalide(client):
    reponse = client.put(
        "/api/parametres-fiscaux/2026",
        json={"methode_tps_tvq": "inconnue"},
    )
    assert reponse.status_code == 422


def test_annee_invalide(client):
    reponse = client.get("/api/parametres-fiscaux/1900")
    assert reponse.status_code == 400
