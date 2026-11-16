from unittest.mock import MagicMock, patch

import pytest

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
from utils.settings import Settings


@pytest.fixture
def mock_settings():
    return MagicMock(spec=Settings)


@pytest.fixture
def mock_system_info_strategy():
    return MagicMock(spec=SystemInformationStrategy)


@pytest.fixture
def mock_station_info_strategy():
    return MagicMock(spec=StationInformationStrategy)


@pytest.fixture
def mock_station_status_strategy():
    return MagicMock(spec=StationStatusStrategy)


@pytest.fixture
def mock_station_aggregator():
    return MagicMock(spec=StationAggregator)


@pytest.fixture
def job_scheduler(
    mock_settings,
    mock_system_info_strategy,
    mock_station_info_strategy,
    mock_station_status_strategy,
    mock_station_aggregator,
):
    return JobScheduler(
        settings=mock_settings,
        system_information_strategy=mock_system_info_strategy,
        station_information_strategy=mock_station_info_strategy,
        station_status_strategy=mock_station_status_strategy,
        station_aggregator=mock_station_aggregator,
    )


def test_job_scheduler_initialization(job_scheduler, mock_settings):
    """Vérifie l'initialisation correcte du JobScheduler et de ses composants."""
    assert job_scheduler.settings == mock_settings
    assert job_scheduler.scheduler is not None
    assert job_scheduler.system_information_strategy is not None
    assert job_scheduler.station_information_strategy is not None
    assert job_scheduler.station_status_strategy is not None
    assert job_scheduler.station_aggregator is not None


def test_job_scheduler_setup_jobs(
    job_scheduler,
    mock_system_info_strategy,
    mock_station_info_strategy,
    mock_station_status_strategy,
    mock_station_aggregator,
):
    """Vérifie que setup_jobs enregistre les 4 tâches avec les bons identifiants et triggers."""
    with patch.object(job_scheduler.scheduler, "add_job") as mock_add_job:
        job_scheduler.setup_jobs()

        assert mock_add_job.call_count == 4
        registered_job_ids = [call.kwargs.get("id") for call in mock_add_job.call_args_list]
        assert "job_system_information" in registered_job_ids
        assert "job_station_information" in registered_job_ids
        assert "job_station_status" in registered_job_ids
        assert "job_station_aggregation" in registered_job_ids

        # Vérification des fonctions passées aux jobs
        funcs = [call.args[0] for call in mock_add_job.call_args_list]
        assert mock_system_info_strategy.execute in funcs
        assert mock_station_info_strategy.execute in funcs
        assert mock_station_status_strategy.execute in funcs
        assert mock_station_aggregator.aggregate_hourly_stats in funcs


def test_job_scheduler_start(job_scheduler):
    """Vérifie que start configure les jobs et démarre le scheduler."""
    with patch.object(job_scheduler, "setup_jobs") as mock_setup_jobs:
        with patch.object(job_scheduler.scheduler, "start") as mock_start:
            job_scheduler.start()
            mock_setup_jobs.assert_called_once()
            mock_start.assert_called_once()


def test_job_scheduler_shutdown(job_scheduler):
    """Vérifie que shutdown arrête le scheduler sans attendre la fin des tâches."""
    with patch.object(job_scheduler.scheduler, "shutdown") as mock_shutdown:
        job_scheduler.shutdown()
        mock_shutdown.assert_called_once_with(wait=False)
