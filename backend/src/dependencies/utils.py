"""Dependency providers for shared database and HTTP clients."""

from functools import lru_cache

import httpx

from utils.db_connection import DbConnection
from utils.settings import get_settings


@lru_cache
def get_db() -> DbConnection:
    """
    Récupère la connexion à la base de données stockée dans l'état de l'application.

    Returns
    -------
    DbConnection
        Instance de connexion à la base de données de l'application.
    """
    settings = get_settings()
    return DbConnection(settings)


@lru_cache
def get_http_client() -> httpx.AsyncClient:
    """
    Récupère le client HTTP asynchrone stocké dans l'état de l'application.

    Returns
    -------
    httpx.AsyncClient
        Instance du client HTTP asynchrone de l'application.
    """
    return httpx.AsyncClient(timeout=15.0)
