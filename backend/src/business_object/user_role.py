from enum import StrEnum


class UserRole(StrEnum):
    """
    Représente le rôle d'un utilisateur dans le système.

    Attributes
    ----------
    ADMIN : str
        L'utilisateur a des privilèges d'administration.
    USER : str
        L'utilisateur a des privilèges d'utilisateur standard.
    """

    ADMIN = "ADMIN"
    USER = "USER"
