from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import parametres

_est_sqlite = parametres.database_url.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _est_sqlite else {}

engine = create_engine(parametres.database_url, connect_args=_connect_args)

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
