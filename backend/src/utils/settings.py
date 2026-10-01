from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Représente la configuration de l'application, chargée depuis l'environnement.

    Parameters
    ----------
    postgres_host : str
        Adresse du serveur PostgreSQL. Requis.
    postgres_port : int
        Port du serveur PostgreSQL. Requis.
    postgres_database : str
        Nom de la base de données PostgreSQL. Requis.
    postgres_user : str
        Nom d'utilisateur PostgreSQL. Requis.
    postgres_password : str
        Mot de passe PostgreSQL. Requis.
    postgres_schema : str
        Schéma PostgreSQL à utiliser. Requis.
    uvicorn_host : str, optional
        Adresse d'écoute du serveur Uvicorn.  Requis, par défaut "127.0.0.1".
    uvicorn_port : int, optional
        Port d'écoute du serveur Uvicorn.  Requis, par défaut 5000.
    """

    postgres_host: str = Field(default=...)
    postgres_port: int = Field(default=...)
    postgres_database: str = Field(default=...)
    postgres_user: str = Field(default=...)
    postgres_password: str = Field(default=...)
    postgres_schema: str = Field(default=...)
    uvicorn_host: str = Field(default="127.0.0.1")
    uvicorn_port: int = Field(default=5000)

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
