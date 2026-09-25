from ..business_object.station_information import StationInformation
from ..service.station_service import StationService


class StationController:
    """Handle station requests."""

    def __init__(self, station_service: StationService):
        self.station_service = station_service

    def get_station_info(self, station_id: str) -> StationInformation:
        """Get station information."""
        raise NotImplementedError

    def list_stations(self, payload: dict) -> list[StationInformation]:
        """List stations."""
        raise NotImplementedError

    def get_station_current_status(self, station_id: str) -> dict:
        """Get current station status."""
        raise NotImplementedError

    def get_station_history(self, payload: dict) -> list[dict]:
        """Get station history."""
        raise NotImplementedError
