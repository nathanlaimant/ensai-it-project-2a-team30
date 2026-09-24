from datetime import datetime

from pydantic import BaseModel


class StationStatus(BaseModel):
    """Describe the historical station status."""

    station_status_id: int
    station_id: str
    num_bikes_available: int
    num_bikes_disabled: int
    num_docks_available: int
    num_docks_disabled: int
    operational_capacity: int
    is_installed: bool
    is_renting: bool
    is_returning: bool
    last_reported: datetime
    vehicle_types_available: list
    vehicle_docks_available: list
    station_state: str
