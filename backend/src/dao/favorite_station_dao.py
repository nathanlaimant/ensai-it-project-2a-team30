from business_object.station_information import StationInformation
from utils.db_connection import DbConnection


class FavoriteStationDAO:
    """Gère l'accès aux données des stations favorites en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def add_favorite(self, user_id: int, station_id: str) -> bool:
        """
        Ajoute une station aux favoris d'un utilisateur.
 
        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
        station_id : str
            Identifiant de la station à ajouter aux favoris.
 
        Returns
        -------
        bool
            True si l'ajout a réussi.
        """
        raise NotImplementedError

    def list_by_user(self, user_id: int) -> list[StationInformation]:
        """
        Liste les stations favorites d'un utilisateur.
 
        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
 
        Returns
        -------
        list of StationInformation
            Liste des stations favorites de l'utilisateur.
        """
        raise NotImplementedError

    def count_favorites(self, station_ids: list[str]) -> dict[str, int]:
        """
        Compte le nombre d'utilisateurs ayant mis chaque station en favori.
 
        Parameters
        ----------
        station_ids : list of str
            Identifiants des stations concernées.
 
        Returns
        -------
        dict
            Dictionnaire associant chaque identifiant de station à son
            nombre de favoris.
        """
        raise NotImplementedError

    def remove_favorite(self, user_id: int, station_id: str) -> bool:
        """
        Retire une station des favoris d'un utilisateur.
 
        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
        station_id : str
            Identifiant de la station à retirer des favoris.
 
        Returns
        -------
        bool
            True si le retrait a réussi.
        """
        raise NotImplementedError
