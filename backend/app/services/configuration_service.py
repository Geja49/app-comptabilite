from sqlalchemy.orm import Session

from app.modeles import Configuration


def obtenir_configuration(session: Session) -> Configuration:
    config = session.get(Configuration, 1)
    if config is None:
        config = Configuration(id=1, redevance_prelevee_source=False)
        session.add(config)
        session.commit()
        session.refresh(config)
    return config
