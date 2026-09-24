from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    """
    Décrit un utilisateur (compte) inscrit sur la plateforme.
 
    Parameters
    ----------
    user_id : int
        Identifiant unique de l'utilisateur.
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
 
    Returns
    -------
    User
        Instance représentant l'utilisateur.
    """

    user_id: int
    username: str
    password_hashed: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    access_token: str
