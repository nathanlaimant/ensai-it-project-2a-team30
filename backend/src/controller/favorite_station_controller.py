from ..business_object.station_information import StationInformation
from ..service.favorite_station_service import FavoriteStationService


class FavoriteStationController:
    """
    Gère les requètes sur les stations favorites.
    
    Parameters
    ----------
    favorite_service : Any
        Service applicatif gérant la logique
        métier liée aux stations favorites.
    """

    def __init__(self, favorite_service: FavoriteStationService):
        self.favorite_service = favorite_service

    def add_favorite(self, station_id: str) -> str:
        """Add a favorite station."""
        raise NotImplementedError

    def list_favorites(self, payload: dict) -> list[StationInformation]:
        """List favorite stations."""
        raise NotImplementedError

    def remove_favorite(self, station_id: str):
        """Remove a favorite station."""
        raise NotImplementedError
