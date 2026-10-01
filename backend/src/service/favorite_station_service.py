from business_object.station_information import StationInformation
from dao.favorite_station_dao import FavoriteStationDAO


class FavoriteStationService:
    """
    Gère la logique métier liée aux stations favorites.

    Parameters
    ----------
    favorite_dao : FavoriteStationDAO
        DAO permettant l'accès aux données des stations favorites.
    """

    def __init__(self, favorite_dao: FavoriteStationDAO):
        self.favorite_dao = favorite_dao

    def add_favorite_station(self, user_id: int, station_id: str) -> bool:
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
        Liste les stations favorites selon des critères de recherche.

        Parameters
        ----------
        query_params : dict
            Critères de filtrage (ex: identifiant de l'utilisateur) et/ou
            de pagination.

        Returns
        -------
        list of StationInformation
            Liste des stations favorites correspondant aux critères.
        """
        raise NotImplementedError

    def remove_favorite_station(self, user_id: int, station_id: str) -> bool:
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
