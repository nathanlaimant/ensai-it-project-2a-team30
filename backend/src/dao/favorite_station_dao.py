from business_object.station_information import StationInformation
from dao.user_dao import UserDAO
from dao.station_dao import StationDAO
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

    def list_favorites(self, query_params: dict) -> list[StationInformation]:
        """
        Liste les stations favorites d'un utilisateur.

        Parameters
        ----------
        query_params: dict
            Identifiant de l'utilisateur, 
            Limite du nombre de stations par page d'affichage
            Nombre de pages maximum à afficher.

        Returns
        -------
        list of StationInformation
            Liste des stations favorites de l'utilisateur.
            Ne renvoie rien si l'utilisateur n'est pas reconnu avec son identifiant.
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
            Ne renvoie rien si un ou plusieurs identifiants de stations ne sont
            pas reconnus.
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
