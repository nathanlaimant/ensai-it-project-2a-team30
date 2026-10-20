"""Dependency providers for data access objects."""

from functools import lru_cache

from dao.favorite_station_dao import FavoriteStationDAO
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from dao.system_information_dao import SystemInformationDAO
from dao.user_dao import UserDAO
from dependencies.utils import get_db


@lru_cache
def get_favorite_station_dao() -> FavoriteStationDAO:
    """Construit une instance de FavoriteStationDAO."""
    return FavoriteStationDAO(get_db())


@lru_cache
def get_station_dao() -> StationDAO:
    """Construit une instance de StationDAO."""
    return StationDAO(get_db())


@lru_cache
def get_station_status_dao() -> StationStatusDAO:
    """Construit une instance de StationStatusDAO."""
    return StationStatusDAO(get_db())


@lru_cache
def get_station_status_hourly_dao() -> StationStatusHourlyDAO:
    """Construit une instance de StationStatusHourlyDAO."""
    return StationStatusHourlyDAO(get_db())


@lru_cache
def get_system_information_dao() -> SystemInformationDAO:
    """Construit une instance de SystemInformationDAO."""
    return SystemInformationDAO(get_db())


@lru_cache
def get_user_dao() -> UserDAO:
    """Construit une instance de UserDAO."""
    return UserDAO(get_db())
