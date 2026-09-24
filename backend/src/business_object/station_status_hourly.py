from datetime import datetime

from pydantic import BaseModel


class StationStatusHourly(BaseModel):
    """Describe aggregated hourly station statistics."""

    station_id: str
    bucket_hour: datetime
    sample_count: int
    avg_operational_capacity: float
    avg_num_bikes_available: float
    avg_num_docks_available: float
    empty_duration_sec: int
    full_duration_sec: int
    empty_events_cnt: int
    full_events_cnt: int
    reliability_score: float
