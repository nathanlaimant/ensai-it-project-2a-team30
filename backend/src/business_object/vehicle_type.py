from pydantic import BaseModel


class VehicleType(BaseModel):
    """Describe a vehicle type."""

    vehicle_type_id: str
    form_factor: str
    rider_capacity: int
    cargo_volume_capacity: int
    cargo_load_capacity: int
    propulsion_type: str
    max_range_meters: float
    name: str
    return_constraint: str
