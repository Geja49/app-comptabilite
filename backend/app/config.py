from pydantic_settings import BaseSettings, SettingsConfigDict


class Parametres(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://comptabilite:comptabilite@localhost:5432/comptabilite"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def liste_cors(self) -> list[str]:
        return [origine.strip() for origine in self.cors_origins.split(",") if origine.strip()]


parametres = Parametres()
