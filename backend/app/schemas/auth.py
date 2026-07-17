from pydantic import BaseModel, EmailStr, Field


class IdentifiantsAuth(BaseModel):
    email: EmailStr
    mot_de_passe: str = Field(min_length=8, max_length=128)


class JetonReponse(BaseModel):
    jeton: str
    type_jeton: str = "Bearer"
    email: str


class UtilisateurReponse(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}


class AuthStatutReponse(BaseModel):
    inscription_ouverte: bool
