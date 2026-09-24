from ..business_object import StationInformation
from ..service import FavoriteStationService


class FavoriteStationController:
    """Handle favorite station requests."""

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
