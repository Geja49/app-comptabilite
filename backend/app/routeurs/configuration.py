from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtenir_session
from app.schemas import ConfigurationReponse, ConfigurationUpdate
from app.services.configuration_service import obtenir_configuration

routeur = APIRouter(prefix="/api/configuration", tags=["configuration"])


@routeur.get("", response_model=ConfigurationReponse)
def lire_configuration(session: Session = Depends(obtenir_session)):
    config = obtenir_configuration(session)
    return ConfigurationReponse(redevance_prelevee_source=config.redevance_prelevee_source)


@routeur.put("", response_model=ConfigurationReponse)
def modifier_configuration(donnees: ConfigurationUpdate, session: Session = Depends(obtenir_session)):
    config = obtenir_configuration(session)
    config.redevance_prelevee_source = donnees.redevance_prelevee_source
    session.commit()
    session.refresh(config)
    return ConfigurationReponse(redevance_prelevee_source=config.redevance_prelevee_source)
