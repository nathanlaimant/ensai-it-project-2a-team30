"""User-related request and response models exposed by the API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from business_object.user_role import UserRole


class SignupRequest(BaseModel):
    """
    Informations nécessaires à l'inscription.

    Parameters
    ----------
    username: str
        Nom d'utilisateur choisi. Requis. Au moins 1 caractère.
    email: EmailStr
        Email de connexion. Requis. Doit être un email valide.
    password: str
        Mot de passe non hashed. Requis. Au moins 1 caractère.
    """

    username: str = Field(default=..., min_length=1)
    email: EmailStr = Field(default=..., min_length=1)
    password: str = Field(default=..., min_length=1)


class LoginRequest(BaseModel):
    """
    Informations nécessaires à l'authentification

    Parameters
    ----------
    username: str
        Nom d'utilisateur. Requis.
    password: str
        Mot de passe non hashed. Requis.
    """

    username: str
    password: str


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
    user_id : int
        Identifiant de l'utilisateur.
    username : str
        Nom d'utilisateur.
    email : str
        Adresse email de l'utilisateur.
    role : UserRole
        Rôle de l'utilisateur dans le système.
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

    user_id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserSearchRequest(BaseModel):
    """
    Critères de recherche pour les utilisateurs (Admin).

    Parameters
    ----------
    username : str | None
        Nom d'utilisateur à rechercher. Nullable.
    email : str | None
        Email à rechercher. Nullable.
    role : str | None
        Rôle à rechercher. Nullable.
    is_active : bool | None
        Statut actif à rechercher. Nullable.
    page : int
        Numéro de page pour la pagination. Doit être >= 1
    size : int
        Nombre d'éléments par page pour la pagination. Doit être entre 1 et 100.
    """

    user_id: int | None = None
    username: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)


class UserUpdateRequest(BaseModel):
    """
    Représente les champs modifiables d'un utilisateur. Au moins un champ doit être fourni.

    Parameters
    ----------
    username : str | None
        Nom d'utilisateur à modifier. Nullable. Au moins 1 caractère si fourni.
    email : EmailStr | None
        Email à modifier. Nullable. Doit être un email valide si fourni.
    password : str | None
        Mot de passe à modifier. Nullable. Au moins 1 caractère si fourni.
    """

    username: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> UserUpdateRequest:
        if not any(v is not None for v in (self.username, self.email, self.password)):
            raise ValueError("At least one profile field must be provided.")
        return self
