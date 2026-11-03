from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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
from utils.log_utils import get_logger, log
from utils.settings import Settings

logger = get_logger(__name__)


class JobScheduler:
    """
    Planifie les tâches récurrentes de l'application (ingestion des
    flux de données et agrégation des statistiques de stations).

    Parameters
    ----------
    settings : Settings
        Configuration de l'application.
    system_information_strategy : SystemInformationStrategy
        Stratégie d'ingestion du flux d'informations système.
    station_information_strategy : StationInformationStrategy
        Stratégie d'ingestion du flux d'informations de stations.
    station_status_strategy : StationStatusStrategy
        Stratégie d'ingestion du flux de statuts de stations.
    station_aggregator : StationAggregator
        Service responsable de l'agrégation horaire des statistiques
        de stations.
    """

    def __init__(
        self,
        settings: Settings,
        system_information_strategy: SystemInformationStrategy,
        station_information_strategy: StationInformationStrategy,
        station_status_strategy: StationStatusStrategy,
        station_aggregator: StationAggregator,
    ):
        self.settings = settings
        self.scheduler = AsyncIOScheduler()

        self.system_information_strategy = system_information_strategy
        self.station_information_strategy = station_information_strategy
        self.station_status_strategy = station_status_strategy

        self.station_aggregator = station_aggregator

    @log
    def setup_jobs(self):
        """
        Enregistre l'ensemble des tâches planifiées dans le scheduler.

        Chaque tâche est ajoutée avec un déclencheur cron (`CronTrigger`) pour
        garantir un alignement régulier et prévisible sur l'horloge système :
        - `job_system_information` : chaque heure à la minute 00 (exécuté immédiatement au démarrage).
        - `job_station_information` : chaque heure à la minute 00 (exécuté immédiatement au démarrage).
        - `job_station_status` : toutes les 5 minutes (:00, :05, :10, ...) (démarrage immédiat).
        - `job_station_aggregation` : chaque heure à la minute 05 pour consolider l'heure écoulée.

        Les options `coalesce=True` et `max_instances=1` garantissent
        qu'une tâche n'est jamais exécutée en parallèle d'elle-même et
        que les exécutions manquées ne s'accumulent pas.

        Returns
        -------
        None
        """
        self.scheduler.add_job(
            self.system_information_strategy.execute,
            trigger=CronTrigger(minute=0),
            id="job_system_information",
            next_run_time=datetime.now(),
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.station_information_strategy.execute,
            trigger=CronTrigger(minute=0),
            id="job_station_information",
            next_run_time=datetime.now(),
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.station_status_strategy.execute,
            trigger=CronTrigger(minute="*/5"),
            id="job_station_status",
            next_run_time=datetime.now(),
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.station_aggregator.aggregate_hourly_stats,
            trigger=CronTrigger(minute=5),
            id="job_station_aggregation",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    @log
    def start(self):
        """
        Démarre le scheduler après avoir enregistré les tâches planifiées.

        Returns
        -------
        None
        """
        self.setup_jobs()
        self.scheduler.start()

    @log
    def shutdown(self):
        """
        Arrête le scheduler sans attendre la fin des tâches en cours.

        Returns
        -------
        None
        """
        self.scheduler.shutdown(wait=False)
