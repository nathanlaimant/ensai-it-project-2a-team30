from ..business_object import StationInformation
from ..dao import StationDAO, StationStatusDAO, StationStatusHourlyDAO


class StationService:
    """Coordinate station and status operations."""

    def __init__(
        self,
        station_dao: StationDAO,
        status_dao: StationStatusDAO,
        hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_dao = station_dao
        self.status_dao = status_dao
        self.hourly_dao = hourly_dao

    def list_stations(self, query_params: dict) -> list[StationInformation]:
        """List stations."""
        raise NotImplementedError

    def get_station_current_status(self, station_id: str) -> dict:
        """Get the current station status."""
        raise NotImplementedError

    def get_station_history(self, query_params: dict) -> list[dict]:
        """Get station history."""
        raise NotImplementedError
