from datetime import date, datetime

from ..business_object import StationStatusHourly


class StationStatusHourlyDAO:
    """Access hourly station statistics."""

    def bulk_insert_hourly_stats(self, records: list[StationStatusHourly]) -> int:
        """Insert hourly records and return the count."""
        raise NotImplementedError

    def get_hourly_stats(self, station_id: str, start_time: datetime, end_time: datetime) -> list[StationStatusHourly]:
        """Find hourly records in a time range."""
        raise NotImplementedError

    def aggregate_daily_stats(self, station_id: str, start_date: date, end_date: date) -> list[dict]:
        """Aggregate hourly records by day."""
        raise NotImplementedError
