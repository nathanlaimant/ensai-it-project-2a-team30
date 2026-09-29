from datetime import datetime


class User:
    """
    Décrit un utilisateur (compte) inscrit sur la plateforme.

    Parameters
    ----------
    user_id : int | None
        Identifiant unique de l'utilisateur. Non-nullable, mais peut être None si l'objet n'a pas été persistée.
    username : str
        Nom d'utilisateur affiché.
    password_hashed : str
        Mot de passe de l'utilisateur, stocké sous forme hachée.
    email : str
        Adresse email de l'utilisateur.
    role : str
        Rôle de l'utilisateur dans le système (ex: "admin", "user").
    is_active : bool
        True si le compte de l'utilisateur est actif.
    created_at : datetime
        Date et heure de création du compte.
    updated_at : datetime
        Date et heure de la dernière mise à jour du compte.
    access_token : str
        Jeton d'accès courant associé à l'utilisateur.
    """

    def __init__(
        self,
        username: str,
        password_hashed: str,
        email: str,
        role: str,
        is_active: bool,
        created_at: datetime,
        updated_at: datetime,
        access_token: str,
        user_id: int | None = None,
    ):
        self.user_id = user_id
        self.username = username
        self.password_hashed = password_hashed
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.access_token = access_token
