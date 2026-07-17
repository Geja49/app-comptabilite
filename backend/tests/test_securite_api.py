from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, obtenir_session
from app.main import app


def _client_avec_db():
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
    return client


def test_sante_sans_cle():
    with TestClient(app) as client:
        reponse = client.get("/api/sante")
        assert reponse.status_code == 200
        assert reponse.json()["statut"] == "ok"


def test_api_refuse_sans_cle():
    with TestClient(app) as client:
        reponse = client.get("/api/parametres-fiscaux/2026")
        assert reponse.status_code == 401


def test_api_accepte_avec_cle():
    client = _client_avec_db()
    try:
        reponse = client.get(
            "/api/parametres-fiscaux/2026",
            headers={"X-API-Key": "cle-test-pytest"},
        )
        assert reponse.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_en_tetes_securite_presents():
    with TestClient(app) as client:
        reponse = client.get("/api/sante")
        assert reponse.headers.get("X-Content-Type-Options") == "nosniff"
        assert reponse.headers.get("X-Frame-Options") == "DENY"
        assert reponse.headers.get("Referrer-Policy") == "no-referrer"
