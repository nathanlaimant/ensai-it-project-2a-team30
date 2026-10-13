"""Dependency providers for authenticated users."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dao.user_dao import UserDAO
from dependencies.dao import get_user_dao
from utils.token_cache import app_token_cache

security = HTTPBearer()


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
    if not persistent_user or persistent_user.user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token.")

    app_token_cache.set(token, persistent_user.user_id)
    return persistent_user.user_id
