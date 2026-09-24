from pydantic import BaseModel


class StationPhysicalCapacity(BaseModel):
    """Describe physical station capacity for a vehicle type."""

    station_id: str
    vehicle_type_id: str
    dock_count: int
