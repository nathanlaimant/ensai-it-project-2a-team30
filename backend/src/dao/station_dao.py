from ..business_object.station_information import StationInformation


class StationDAO:
    """Access station information."""

    def upsert_station_info(self, station: StationInformation) -> bool:
        """Insert or update station information."""
        raise NotImplementedError

    def get_by_id(self, station_id: str) -> StationInformation:
        """Find a station by identifier."""
        raise NotImplementedError

    def get_nearby(
        self, lat: float, lon: float, radius_meters: float
    ) -> list[StationInformation]:
        """Find stations near a position."""
        raise NotImplementedError

    def list_stations(self, query_params: dict) -> list[StationInformation]:
        """List stations matching query parameters."""
        raise NotImplementedError
