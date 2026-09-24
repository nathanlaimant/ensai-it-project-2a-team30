from ..business_object import StationInformation
from ..dao import FavoriteStationDAO


class FavoriteStationService:
    """Coordinate favorite station operations."""

    def __init__(self, favorite_dao: FavoriteStationDAO):
        self.favorite_dao = favorite_dao

    def add_favorite_station(self, user_id: int, station_id: str) -> bool:
        """Add a favorite station."""
        raise NotImplementedError

    def list_favorites(self, query_params: dict) -> list[StationInformation]:
        """List favorite stations."""
        raise NotImplementedError

    def remove_favorite_station(self, user_id: int, station_id: str) -> bool:
        """Remove a favorite station."""
        raise NotImplementedError
