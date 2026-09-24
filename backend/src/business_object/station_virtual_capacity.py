from pydantic import BaseModel


class StationVirtualCapacity(BaseModel):
    """Describe virtual station capacity for a vehicle type."""

    station_id: str
    vehicle_type_id: str
    capacity: int
