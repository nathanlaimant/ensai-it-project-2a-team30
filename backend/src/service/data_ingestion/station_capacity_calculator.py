from ..business_object import StationStatus


class StationCapacityCalculator:
    """Calculate station operational capacity."""

    def calculate_capacity(self, station_status: StationStatus) -> int:
        """Return the operational capacity."""
        raise NotImplementedError
