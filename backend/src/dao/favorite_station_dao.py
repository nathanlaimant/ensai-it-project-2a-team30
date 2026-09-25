from ..business_object.station_information import StationInformation


class FavoriteStationDAO:
    """Access favorite station records."""

    def add_favorite(self, user_id: int, station_id: str) -> bool:
        """Add a station to a user's favorites."""
        raise NotImplementedError

    def list_by_user(self, user_id: int) -> list[StationInformation]:
        """List a user's favorite stations."""
        raise NotImplementedError

    def count_favorites(self, station_ids: list[str]) -> dict[str, int]:
        """Count favorites for stations."""
        raise NotImplementedError

    def remove_favorite(self, user_id: int, station_id: str) -> bool:
        """Remove a station from a user's favorites."""
        raise NotImplementedError
