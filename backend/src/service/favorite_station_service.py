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
        return self.favorite_dao.add_favorite(user_id, station_id)

    def list_favorites(
        self, user_id: int, page: int = 1, size: int = 10
    ) -> list[StationInformation] | None:
        """
        Liste les stations favorites selon des critères de recherche.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
        page : int
            Numéro de la page à récupérer.
        size : int
            Nombre de stations par page.

        Returns
        -------
        list of StationInformation
            Liste des stations favorites correspondant aux critères.
            Ne renvoie rien si l'utilisateur n'est pas reconnu.
        """
        return self.favorite_dao.list_favorites(user_id, page, size)

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
        return self.favorite_dao.remove_favorite(user_id, station_id)
