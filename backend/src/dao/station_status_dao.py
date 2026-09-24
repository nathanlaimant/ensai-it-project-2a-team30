from datetime import datetime

from ..business_object import StationStatus


class StationStatusDAO:
    """Access station status records."""

    def bulk_insert_status(self, records: list[StationStatus]) -> int:
        """Insert status records and return the count."""
        raise NotImplementedError

    def get_latest_status(self, station_id: str) -> StationStatus:
        """Find the latest status for a station."""
        raise NotImplementedError

    def get_status_history(self, station_id: str, start_time: datetime, end_time: datetime) -> list[StationStatus]:
        """Find status records in a time range."""
        raise NotImplementedError
