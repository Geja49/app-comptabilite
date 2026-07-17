from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import parametres

_est_sqlite = parametres.database_url.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _est_sqlite else {}

# Neon / Supabase exigent souvent SSL
_url = parametres.database_url
if not _est_sqlite and "sslmode=" not in _url:
    separateur = "&" if "?" in _url else "?"
    _url = f"{_url}{separateur}sslmode=require"

engine = create_engine(_url, connect_args=_connect_args)

if _est_sqlite:

    @event.listens_for(engine, "connect")
    def _activer_cles_etrangeres(connexion, _record):
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys=ON")
        curseur.close()


SessionLocale = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtenir_session():
    session = SessionLocale()
    try:
        yield session
    finally:
        session.close()
