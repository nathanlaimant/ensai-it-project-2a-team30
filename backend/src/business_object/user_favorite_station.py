from datetime import datetime


class UserFavoriteStation:
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
    """

    def __init__(self, user_id: int, station_id: str, created_at: datetime):
        self.user_id = user_id
        self.station_id = station_id
        self.created_at = created_at
