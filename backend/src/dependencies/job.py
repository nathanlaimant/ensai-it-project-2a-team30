"""Dependency providers for scheduled jobs."""

from functools import lru_cache

from dependencies.dao import (
    get_station_dao,
    get_station_status_dao,
    get_station_status_hourly_dao,
    get_system_information_dao,
)
from dependencies.utils import get_http_client
from service.schedule.data_aggregation.station_aggregator import StationAggregator
from service.schedule.data_ingestion.station_information_strategy import (
    StationInformationStrategy,
)
from service.schedule.data_ingestion.station_status_strategy import (
    StationStatusStrategy,
)
from service.schedule.data_ingestion.system_information_strategy import (
    SystemInformationStrategy,
)
from service.schedule.job_scheduler import JobScheduler
from utils.settings import get_settings


@lru_cache
def get_system_information_strategy() -> SystemInformationStrategy:
    """Construit une instance de SystemInformationStrategy."""
    return SystemInformationStrategy(
        dao=get_system_information_dao(),
        feed_name="system_information",
        url=get_settings().system_information_feed_url,
        http_client=get_http_client(),
    )


@lru_cache
def get_station_information_strategy() -> StationInformationStrategy:
    """Construit une instance de StationInformationStrategy."""
    return StationInformationStrategy(
        dao=get_station_dao(),
        feed_name="station_information",
        url=get_settings().station_information_feed_url,
        http_client=get_http_client(),
    )


@lru_cache
def get_station_status_strategy() -> StationStatusStrategy:
    """Construit une instance de StationStatusStrategy."""
    return StationStatusStrategy(
        dao=get_station_status_dao(),
        feed_name="station_status",
        url=get_settings().station_status_feed_url,
        http_client=get_http_client(),
    )


@lru_cache
def get_station_aggregator() -> StationAggregator:
    """Construit une instance de StationAggregator."""
    return StationAggregator(
        station_status_dao=get_station_status_dao(),
        station_hourly_dao=get_station_status_hourly_dao(),
    )


@lru_cache
def get_job_scheduler() -> JobScheduler:
    """Construit une instance de JobScheduler."""
    return JobScheduler(
        settings=get_settings(),
        system_information_strategy=get_system_information_strategy(),
        station_information_strategy=get_station_information_strategy(),
        station_status_strategy=get_station_status_strategy(),
        station_aggregator=get_station_aggregator(),
    )
