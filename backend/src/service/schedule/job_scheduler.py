from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

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
from service.schedule.data_ingestion.vehicle_type_strategy import VehicleTypeStrategy
from utils.settings import Settings


class JobScheduler:
    """Schedule recurring application jobs."""

    def __init__(
        self,
        settings: Settings,
        system_information_strategy: SystemInformationStrategy,
        station_information_strategy: StationInformationStrategy,
        vehicle_type_strategy: VehicleTypeStrategy,
        station_status_strategy: StationStatusStrategy,
        station_aggregator: StationAggregator,
    ):
        self.settings = settings
        self.scheduler = AsyncIOScheduler()

        self.system_information_strategy = system_information_strategy
        self.station_information_strategy = station_information_strategy
        self.vehicle_type_strategy = vehicle_type_strategy
        self.station_status_strategy = station_status_strategy

        self.station_aggregator = station_aggregator

    def setup_jobs(self):
        """Schedule jobs."""
        self.scheduler.add_job(
            self.system_information_strategy.execute,
            trigger=IntervalTrigger(
                seconds=self.settings.system_information_interval_seconds
            ),
            id="job_system_information",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.station_information_strategy.execute,
            trigger=IntervalTrigger(
                seconds=self.settings.station_information_interval_seconds
            ),
            id="job_station_information",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.vehicle_type_strategy.execute,
            trigger=IntervalTrigger(
                seconds=self.settings.vehicle_type_interval_seconds
            ),
            id="job_vehicle_type",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.station_status_strategy.execute,
            trigger=IntervalTrigger(
                seconds=self.settings.station_status_interval_seconds
            ),
            id="job_station_status",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.station_aggregator.aggregate_hourly_stats,
            trigger=IntervalTrigger(
                seconds=self.settings.station_aggregation_interval_seconds
            ),
            id="job_station_aggregation",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    def start(self):
        """Start scheduled jobs."""
        self.setup_jobs()
        self.scheduler.start()

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown(wait=False)
