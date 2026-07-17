from pydantic_settings import BaseSettings, SettingsConfigDict


class Parametres(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pas de mot de passe en dur : définir DATABASE_URL dans .env
    database_url: str = "sqlite:///./comptabilite.db"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    # Conservé en secours si JWT_SECRET est vide (transition)
    api_cle: str = ""
    jwt_secret: str = ""
    jwt_duree_heures: int = 12
    admin_email: str = ""
    admin_mot_de_passe: str = ""
    environnement: str = "developpement"
    # Limite du corps JSON (octets) — protège contre les requêtes trop volumineuses
    taille_max_corps: int = 1_048_576

    @property
    def liste_cors(self) -> list[str]:
        return [origine.strip() for origine in self.cors_origins.split(",") if origine.strip()]

    @property
    def est_production(self) -> bool:
        return self.environnement.lower() in {"production", "prod"}


parametres = Parametres()
