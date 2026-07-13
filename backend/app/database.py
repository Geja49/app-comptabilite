from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import parametres

engine = create_engine(parametres.database_url)
SessionLocale = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtenir_session():
    session = SessionLocale()
    try:
        yield session
    finally:
        session.close()
