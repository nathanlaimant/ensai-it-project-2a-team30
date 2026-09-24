from ..dao import StationStatusDAO, StationStatusHourlyDAO


class StationAggregationService:
    """Aggregate station statuses into hourly statistics."""

    def __init__(
        self,
        station_status_dao: StationStatusDAO,
        station_hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_status_dao = station_status_dao
        self.station_hourly_dao = station_hourly_dao

    def aggregate_hourly_stats(self) -> int:
        """Aggregate hourly station statistics."""
        raise NotImplementedError
