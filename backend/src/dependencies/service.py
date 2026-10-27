"""Dependency providers for application services."""

from fastapi import Depends

from dependencies.dao import get_station_dao, get_station_status_dao, get_station_status_hourly_dao, get_user_dao
from service.recommendation_service import RecommendationService
from service.station_service import StationService
from service.user_service import UserService


def get_user_service(
    user_dao=Depends(get_user_dao),
) -> UserService:
    """Construit une instance de UserService."""
    return UserService(user_dao)


def get_station_service(station_dao=Depends(get_station_dao)) -> StationService:
    """Construit une instance de StationService"""
    return StationService(station_dao)


def get_recommendation_service(
    station_dao=Depends(get_station_dao),
    status_dao=Depends(get_station_status_dao),
    hourly_dao=Depends(get_station_status_hourly_dao)
) -> RecommendationService:
    """Construit une instance de RecommendationService"""
    return RecommendationService(station_dao, status_dao, hourly_dao)
