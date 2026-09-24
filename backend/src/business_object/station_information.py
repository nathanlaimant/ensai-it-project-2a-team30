from pydantic import BaseModel


class StationInformation(BaseModel):
    """Describe a station and its fixed properties."""

    station_id: str
    name: str
    short_name: str
    lat: float
    lon: float
    address: str
    is_virtual_station: bool
    station_area: dict
    contact_phone: str
    capacity: int
    is_charging_station: bool
