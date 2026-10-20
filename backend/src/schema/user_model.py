"""User-related request and response models exposed by the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginResponse(BaseModel):
    """
    Informations de session retournées après une authentification réussie.

    Parameters
    ----------
    user_id : int
        Identifiant de l'utilisateur authentifié.
    username : str
        Nom d'utilisateur de l'utilisateur authentifié.
    access_token : str
        Jeton d'accès de la session créée.

    Returns
    -------
    LoginResponse
        Instance représentant les informations de session.
    """

    user_id: int
    username: str
    access_token: str


class UserResponse(BaseModel):
    """
    Informations publiques d'un utilisateur. Les identifiants
    d'authentification et les jetons de session ne sont pas exposés.

    Parameters
    ----------
    user_id : int, optional
        Identifiant de l'utilisateur.
    username : str
        Nom d'utilisateur.
    email : str
        Adresse email de l'utilisateur.
    role : str
        Rôle de l'utilisateur dans le système (ex: "ADMIN", "USER").
    is_active : bool
        True si le compte de l'utilisateur est actif.
    created_at : datetime
        Date et heure de création du compte.
    updated_at : datetime
        Date et heure de la dernière mise à jour du compte.

    Returns
    -------
    UserResponse
        Instance représentant les informations publiques de l'utilisateur.
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: int | None
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
