from ..business_object import StationStatus


class StationStateDurationCalculator:
    """Calculate station state durations."""

    def calculate_durations(self, station_status: list[StationStatus]) -> list[dict]:
        """Calculate durations from status records."""
        raise NotImplementedError
