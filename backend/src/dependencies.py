"""
Module: dependencies.py
 
Fonctions de dépendance FastAPI (injection de dépendances) permettant
de construire et fournir les instances de connexion base de données,
DAO, services et utilisateur courant authentifié aux endpoints de
l'application.
"""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dao.favorite_station_dao import FavoriteStationDAO
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from dao.user_dao import UserDAO
from service.user_service import UserService
from utils.db_connection import DbConnection
from utils.token_cache import app_token_cache

security = HTTPBearer()


def get_db(request: Request) -> DbConnection:
    """
    Récupère la connexion à la base de données stockée dans l'état de l'application.
 
    Parameters
    ----------
    request : Request
        Requête HTTP entrante, dont l'état de l'application (`app.state`)
        contient l'instance de connexion à la base de données.
 
    Returns
    -------
    DbConnection
        Instance de connexion à la base de données de l'application.
    """
    return request.app.state.db


def get_favorite_station_dao(
    db: DbConnection = Depends(get_db),
) -> FavoriteStationDAO:
    """
    Construit une instance de FavoriteStationDAO.
 
    Parameters
    ----------
    db : DbConnection
        Connexion à la base de données, injectée via `get_db`.
 
    Returns
    -------
    FavoriteStationDAO
        Instance du DAO des stations favorites.
    """
    return FavoriteStationDAO(db)


def get_station_dao(
    db: DbConnection = Depends(get_db),
) -> StationDAO:
    """
    Construit une instance de StationDAO.
 
    Parameters
    ----------
    db : DbConnection
        Connexion à la base de données, injectée via `get_db`.
 
    Returns
    -------
    StationDAO
        Instance du DAO des stations.
    """
    return StationDAO(db)


def get_station_status_dao(
    db: DbConnection = Depends(get_db),
) -> StationStatusDAO:
    """
    Construit une instance de StationStatusDAO.
 
    Parameters
    ----------
    db : DbConnection
        Connexion à la base de données, injectée via `get_db`.
 
    Returns
    -------
    StationStatusDAO
        Instance du DAO des statuts de stations.
    """
    return StationStatusDAO(db)


def get_station_status_hourly_dao(
    db: DbConnection = Depends(get_db),
) -> StationStatusHourlyDAO:
    """
    Construit une instance de StationStatusHourlyDAO.
 
    Parameters
    ----------
    db : DbConnection
        Connexion à la base de données, injectée via `get_db`.
 
    Returns
    -------
    StationStatusHourlyDAO
        Instance du DAO des agrégations horaires de statut de stations.
    """
    return StationStatusHourlyDAO(db)


def get_user_dao(
    db: DbConnection = Depends(get_db),
) -> UserDAO:
    """
    Construit une instance de UserDAO.
 
    Parameters
    ----------
    db : DbConnection
        Connexion à la base de données, injectée via `get_db`.
 
    Returns
    -------
    UserDAO
        Instance du DAO des utilisateurs.
    """
    return UserDAO(db)


def get_user_service(
    user_dao: UserDAO = Depends(get_user_dao),
) -> UserService:
    """
    Construit une instance de UserService.
 
    Parameters
    ----------
    user_dao : UserDAO
        DAO des utilisateurs, injecté via `get_user_dao`.
 
    Returns
    -------
    UserService
        Instance du service applicatif des utilisateurs.
    """
    return UserService(user_dao)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_dao: UserDAO = Depends(get_user_dao),
) -> int:
    """
    Résout l'utilisateur courant à partir du jeton d'authentification.
 
    Vérifie d'abord si le jeton est présent dans le cache en mémoire
    (`app_token_cache`) ; sinon, recherche l'utilisateur en base de
    données via le DAO puis met à jour le cache pour les prochains appels.
 
    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Identifiants d'autorisation HTTP (schéma Bearer), injectés via
        `security`.
    user_dao : UserDAO
        DAO des utilisateurs, injecté via `get_user_dao`.
 
    Returns
    -------
    int
        Identifiant de l'utilisateur authentifié.
 
    Raises
    ------
    HTTPException
        Levée avec le code 401 si le jeton est invalide ou ne correspond
        à aucun utilisateur.
    """
    token = credentials.credentials

    cached_user_id = app_token_cache.get(token)
    if cached_user_id:
        return cached_user_id

    persistent_user = user_dao.get_by_access_token(token)
    if not persistent_user:
        raise HTTPException(status_code=401, detail="Invalid token.")

    app_token_cache.set(token, persistent_user.user_id)
    return persistent_user.user_id
