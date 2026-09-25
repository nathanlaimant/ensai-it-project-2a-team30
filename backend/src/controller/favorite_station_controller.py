"""Gère les requètes sur les stations favorites."""

from business_object.station_information import StationInformation
from service.favorite_station_service import FavoriteStationService


def add_favorite(station_id: str) -> str:
    """Add a favorite station."""
    raise NotImplementedError


def list_favorites(payload: dict) -> list[StationInformation]:
    """List favorite stations."""
    raise NotImplementedError


def remove_favorite(station_id: str):
    """Remove a favorite station."""
    raise NotImplementedError
