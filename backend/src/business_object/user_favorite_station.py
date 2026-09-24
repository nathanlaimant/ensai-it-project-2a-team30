from datetime import datetime

from pydantic import BaseModel


class UserFavoriteStation(BaseModel):
    """
    Décrit une station marquée comme favorite par un utilisateur.
 
    Parameters
    ----------
    user_id : int
        Identifiant de l'utilisateur.
    station_id : str
        Identifiant de la station marquée comme favorite.
    created_at : datetime
        Date et heure à laquelle la station a été ajoutée aux favoris.
 
    Returns
    -------
    UserFavoriteStation
        Instance représentant l'association utilisateur/station favorite.
    """

    user_id: int
    station_id: str
    created_at: datetime
