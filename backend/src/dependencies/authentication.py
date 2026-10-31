"""Dependency providers for authenticated users."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dao.user_dao import UserDAO
from dependencies.dao import get_user_dao
from utils.token_cache import app_token_cache

security = HTTPBearer()


def get_current_user_and_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_dao: UserDAO = Depends(get_user_dao),
) -> tuple[int, str]:
    """
    Résout l'utilisateur courant à partir du jeton d'authentification.

    Vérifie d'abord si le jeton est présent dans le cache en mémoire
    (`app_token_cache`) ; sinon, recherche l'utilisateur actif en base de
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
    tuple[int, str]
        Tuple contenant l'identifiant de l'utilisateur authentifié et son rôle.

    Raises
    ------
    HTTPException
        Levée avec le code 401 si le jeton est invalide ou ne correspond
        à aucun utilisateur.
    """
    token = credentials.credentials

    cached = app_token_cache.get(token)
    if cached:
        return cached

    persistent_user = user_dao.get_by_access_token(token)
    if not persistent_user or persistent_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    if not persistent_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive.",
        )

    user_data = (persistent_user.user_id, persistent_user.role)
    app_token_cache.set(token, user_data)
    return user_data


def get_current_user(
    user_and_role: tuple[int, str] = Depends(get_current_user_and_role),
) -> int:
    """Returns the authenticated user_id."""
    return user_and_role[0]


def get_current_admin(
    user_and_role: tuple[int, str] = Depends(get_current_user_and_role),
) -> int:
    """Returns the authenticated admin user_id, or raises 403 Forbidden."""
    user_id, role = user_and_role
    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required.",
        )
    return user_id
