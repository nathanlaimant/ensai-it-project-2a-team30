from ..business_object import StationStatusHourly


class StationReliabilityCalculator:
    """Calculate station reliability."""

    def calculate_reliability(
        self, station_status_hourly: StationStatusHourly
    ) -> float:
        """Return a reliability score."""
        raise NotImplementedError
