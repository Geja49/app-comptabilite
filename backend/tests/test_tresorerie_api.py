from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, obtenir_session
from app.main import app

EMAIL = "treso@example.com"
MDP = "MotDePasse123"


def _client():
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
    client = TestClient(app)
    inscription = client.post(
        "/api/auth/inscription",
        json={"email": EMAIL, "mot_de_passe": MDP},
    )
    assert inscription.status_code == 201
    client.headers.update({"Authorization": f"Bearer {inscription.json()['jeton']}"})
    return client


def test_resume_cree_comptes_par_defaut():
    client = _client()
    try:
        reponse = client.get("/api/tresorerie/resume")
        assert reponse.status_code == 200
        data = reponse.json()
        assert len(data["comptes"]) == 2
        assert Decimal(data["total_tresorerie"]) == Decimal("0")
        types = {c["type_compte"] for c in data["comptes"]}
        assert types == {"caisse", "banque"}
    finally:
        app.dependency_overrides.clear()


def test_encaissement_et_depot():
    client = _client()
    try:
        resume = client.get("/api/tresorerie/resume").json()
        caisse = next(c for c in resume["comptes"] if c["type_compte"] == "caisse")
        banque = next(c for c in resume["comptes"] if c["type_compte"] == "banque")

        enc = client.post(
            "/api/tresorerie/operations",
            json={
                "date_operation": "2026-07-16",
                "type_operation": "encaissement",
                "compte_id": caisse["id"],
                "montant": "250.00",
                "libelle": "Encaissement journée",
            },
        )
        assert enc.status_code == 201

        resume2 = client.get("/api/tresorerie/resume").json()
        assert Decimal(resume2["total_caisse"]) == Decimal("250.00")
        assert Decimal(resume2["total_banque"]) == Decimal("0")

        depot = client.post(
            "/api/tresorerie/operations",
            json={
                "date_operation": "2026-07-16",
                "type_operation": "depot",
                "compte_id": caisse["id"],
                "compte_contrepartie_id": banque["id"],
                "montant": "200.00",
                "libelle": "Dépôt bancaire",
                "reference": "BORD-001",
            },
        )
        assert depot.status_code == 201
        assert len(depot.json()) == 2

        resume3 = client.get("/api/tresorerie/resume").json()
        assert Decimal(resume3["total_caisse"]) == Decimal("50.00")
        assert Decimal(resume3["total_banque"]) == Decimal("200.00")
        assert Decimal(resume3["total_tresorerie"]) == Decimal("250.00")
    finally:
        app.dependency_overrides.clear()


def test_paiement_diminue_solde():
    client = _client()
    try:
        resume = client.get("/api/tresorerie/resume").json()
        banque = next(c for c in resume["comptes"] if c["type_compte"] == "banque")
        client.post(
            "/api/tresorerie/operations",
            json={
                "date_operation": str(date.today()),
                "type_operation": "encaissement",
                "compte_id": banque["id"],
                "montant": "100.00",
                "libelle": "Dépôt initial",
            },
        )
        client.post(
            "/api/tresorerie/operations",
            json={
                "date_operation": str(date.today()),
                "type_operation": "paiement",
                "compte_id": banque["id"],
                "montant": "40.00",
                "libelle": "Paiement essence",
            },
        )
        final = client.get("/api/tresorerie/resume").json()
        assert Decimal(final["total_banque"]) == Decimal("60.00")
    finally:
        app.dependency_overrides.clear()
