from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, obtenir_session
from app.main import app

EMAIL = "admin@example.com"
MDP = "MotDePasse123"


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


def _jeton(client: TestClient) -> str:
    reponse = client.post(
        "/api/auth/inscription",
        json={"email": EMAIL, "mot_de_passe": MDP},
    )
    assert reponse.status_code == 201, reponse.text
    return reponse.json()["jeton"]


def test_sante_sans_auth():
    with TestClient(app) as client:
        reponse = client.get("/api/sante")
        assert reponse.status_code == 200
        assert reponse.json()["statut"] == "ok"


def test_api_refuse_sans_jeton():
    with TestClient(app) as client:
        reponse = client.get("/api/parametres-fiscaux/2026")
        assert reponse.status_code == 401


def test_api_accepte_avec_jeton():
    client = _client_avec_db()
    try:
        jeton = _jeton(client)
        reponse = client.get(
            "/api/parametres-fiscaux/2026",
            headers={"Authorization": f"Bearer {jeton}"},
        )
        assert reponse.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_connexion_apres_inscription():
    client = _client_avec_db()
    try:
        _jeton(client)
        reponse = client.post(
            "/api/auth/connexion",
            json={"email": EMAIL, "mot_de_passe": MDP},
        )
        assert reponse.status_code == 200
        assert reponse.json()["jeton"]
    finally:
        app.dependency_overrides.clear()


def test_inscription_fermee_apres_premier_compte():
    client = _client_avec_db()
    try:
        _jeton(client)
        reponse = client.post(
            "/api/auth/inscription",
            json={"email": "autre@example.com", "mot_de_passe": MDP},
        )
        assert reponse.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_en_tetes_securite_presents():
    with TestClient(app) as client:
        reponse = client.get("/api/sante")
        assert reponse.headers.get("X-Content-Type-Options") == "nosniff"
        assert reponse.headers.get("X-Frame-Options") == "DENY"
        assert reponse.headers.get("Referrer-Policy") == "no-referrer"


def test_corps_trop_volumineux_refuse():
    client = _client_avec_db()
    try:
        jeton = _jeton(client)
        reponse = client.post(
            "/api/categories",
            headers={
                "Authorization": f"Bearer {jeton}",
                "Content-Type": "application/json",
                "Content-Length": str(2_000_000),
            },
            content=b"{}",
        )
        assert reponse.status_code == 413
    finally:
        app.dependency_overrides.clear()


def test_pagination_categories_limite_max():
    client = _client_avec_db()
    try:
        jeton = _jeton(client)
        reponse = client.get(
            "/api/categories",
            params={"limite": 9999},
            headers={"Authorization": f"Bearer {jeton}"},
        )
        assert reponse.status_code == 422
    finally:
        app.dependency_overrides.clear()
