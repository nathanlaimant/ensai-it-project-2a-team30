"""Gère les consultations de stations."""

from ..business_object.station_information import StationInformation
from ..service.station_service import StationService


def get_station_info(station_id: str) -> StationInformation:
    """Get station information."""
    raise NotImplementedError


def list_stations(payload: dict) -> list[StationInformation]:
    """List stations."""
    raise NotImplementedError


def get_station_current_status(station_id: str) -> dict:
    """Get current station status."""
    raise NotImplementedError


def get_station_history(payload: dict) -> list[dict]:
    """Get station history."""
    raise NotImplementedError
