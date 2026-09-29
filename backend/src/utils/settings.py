from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Représente la configuration de l'application, chargée depuis l'environnement.
 
    Parameters
    ----------
    postgres_host : str
        Adresse du serveur PostgreSQL.
    postgres_port : int
        Port du serveur PostgreSQL.
    postgres_database : str
        Nom de la base de données PostgreSQL.
    postgres_user : str
        Nom d'utilisateur PostgreSQL.
    postgres_password : str
        Mot de passe PostgreSQL.
    postgres_schema : str
        Schéma PostgreSQL à utiliser.
    uvicorn_host : str, optional
        Adresse d'écoute du serveur Uvicorn. Par défaut "127.0.0.1".
    uvicorn_port : int, optional
        Port d'écoute du serveur Uvicorn. Par défaut 5000.
 
    Returns
    -------
    Settings
        Instance représentant la configuration de l'application.
    """
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str
    postgres_schema: str
    uvicorn_host: str = "127.0.0.1"
    uvicorn_port: int = 5000

    settings_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne l'instance de configuration de l'application, mise en cache.
 
    L'utilisation de `lru_cache` garantit qu'une seule instance de
    `Settings` est créée et réutilisée sur la durée de vie de l'application.
 
    Returns
    -------
    Settings
        Instance de configuration de l'application.
    """
    return Settings()
