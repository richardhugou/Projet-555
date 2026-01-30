from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str

    # Identifiants API (pour l'initialisation et les tests)
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "secret"  # Valeur par défaut pour dev

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" # Ignore les variables en trop dans le .env
        case_sensitive = True # Important sur Windows

settings = Settings()
