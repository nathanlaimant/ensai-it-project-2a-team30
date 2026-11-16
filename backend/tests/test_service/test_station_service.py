from datetime import UTC, date, datetime
from unittest.mock import MagicMock

import pytest

from business_object.station_information import StationInformation
from business_object.station_state import StationState
from business_object.station_status import StationStatus
from business_object.station_status_hourly import StationStatusHourly
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from schema.common_model import TimePeriod
from schema.station_model import (
    StationRecommendationRequest,
    StationSearchRequest,
    VehicleTypeFilter,
)
from service.station_service import StationService


@pytest.fixture
def station_dao():
    return MagicMock(spec=StationDAO)


@pytest.fixture
def status_dao():
    return MagicMock(spec=StationStatusDAO)


@pytest.fixture
def hourly_dao():
    return MagicMock(spec=StationStatusHourlyDAO)


@pytest.fixture
def station_service(station_dao, status_dao, hourly_dao):
    return StationService(station_dao, status_dao, hourly_dao)


# Fixtures d'objets pour les tests
@pytest.fixture
def sample_station():
    return StationInformation(
        station_id="st_101",
        name="Station Châtelet",
        short_name="CH101",
        lat=48.8584,
        lon=2.3470,
        address="Place du Châtelet",
        is_virtual_station=False,
        station_area=None,
        contact_phone=None,
        capacity=30,
        is_charging_station=True,
    )


@pytest.fixture
def sample_status():
    return StationStatus(
        station_id="st_101",
        num_bikes_available=10,
        num_bikes_disabled=0,
        num_docks_available=20,
        num_docks_disabled=0,
        operational_capacity=30,
        last_reported=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        vehicle_types_available={"mechanical": 6, "electric": 4},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
        station_status_id=1,
    )


@pytest.fixture
def sample_hourly_status():
    return StationStatusHourly(
        station_id="st_101",
        bucket_hour=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        sample_count=12,
        avg_operational_capacity=30.0,
        avg_num_bikes_available=10.0,
        avg_num_docks_available=20.0,
        empty_duration_sec=300,
        full_duration_sec=600,
        empty_events_cnt=1,
        full_events_cnt=2,
        reliability_score=85.5,
    )


# --- Tests de get_by_id() ---


def test_get_by_id_ok(station_service, station_dao, sample_station):
    """Retourne la station correspondante à l'identifiant."""
    station_dao.get_by_id.return_value = sample_station
    result = station_service.get_by_id("st_101")
    assert result == sample_station
    station_dao.get_by_id.assert_called_once_with("st_101")


def test_get_by_id_not_found(station_service, station_dao):
    """Retourne None si la station n'existe pas."""
    station_dao.get_by_id.return_value = None
    assert station_service.get_by_id("unknown") is None


def test_get_by_id_empty_id(station_service, station_dao):
    """Retourne None directement si l'identifiant est vide ou falsy."""
    assert station_service.get_by_id("") is None
    station_dao.get_by_id.assert_not_called()


# --- Tests de list_stations() ---


def test_list_stations_ok(station_service, station_dao, sample_station):
    """Transmet les critères de StationSearchRequest au DAO."""
    req = StationSearchRequest(
        name="Châtelet",
        short_name="CH",
        address="Place",
        min_capacity=20,
        max_capacity=40,
        page=2,
        size=15,
    )
    station_dao.list_stations.return_value = [sample_station]

    result = station_service.list_stations(req)

    assert result == [sample_station]
    station_dao.list_stations.assert_called_once_with(
        name="Châtelet",
        short_name="CH",
        address="Place",
        min_capacity=20,
        max_capacity=40,
        page=2,
        size=15,
    )


def test_list_stations_empty_payload(station_service, station_dao):
    """Retourne [] si le payload est falsy."""
    assert station_service.list_stations(None) == []
    station_dao.list_stations.assert_not_called()


# --- Tests de _compute_full_ratio() ---


def test_compute_full_ratio():
    """Vérifie le calcul borné du ratio de remplissage."""
    assert StationService._compute_full_ratio(10, 20) == 0.5
    assert StationService._compute_full_ratio(25, 20) == 1.0
    assert StationService._compute_full_ratio(5, 0) == 0.0


# --- Tests de get_station_current_status() ---


def test_get_station_current_status_ok(station_service, status_dao, hourly_dao, sample_status, sample_hourly_status):
    """Récupère l'état courant et le score de fiabilité récent."""
    status_dao.get_latest_status.return_value = sample_status
    hourly_dao.get_latest_hourly_status.return_value = sample_hourly_status

    res = station_service.get_station_current_status("st_101")

    assert res is not None
    assert res["num_bikes_available"] == 10
    assert res["num_docks_available"] == 20
    assert res["full_ratio"] == pytest.approx(10 / 30)
    assert res["reliability_score"] == 85.5


def test_get_station_current_status_without_hourly(station_service, status_dao, hourly_dao, sample_status):
    """Récupère l'état courant même en l'absence de statut horaire."""
    status_dao.get_latest_status.return_value = sample_status
    hourly_dao.get_latest_hourly_status.return_value = None

    res = station_service.get_station_current_status("st_101")

    assert res is not None
    assert res["reliability_score"] is None


def test_get_station_current_status_not_found(station_service, status_dao):
    """Retourne None si le statut courant n'est pas trouvé."""
    status_dao.get_latest_status.return_value = None
    assert station_service.get_station_current_status("st_ghost") is None


# --- Tests de get_stations_current_statuses() ---


def test_get_stations_current_statuses_ok(station_service, status_dao, hourly_dao, sample_status, sample_hourly_status):
    """Récupère l'état de plusieurs stations avec suppression des doublons et IDs vides."""
    status_dao.get_latest_statuses.return_value = {"st_101": sample_status}
    hourly_dao.get_latest_hourly_statuses.return_value = {"st_101": sample_hourly_status}

    res = station_service.get_stations_current_statuses(["st_101", "st_101", ""])

    assert "st_101" in res
    assert res["st_101"]["num_bikes_available"] == 10
    assert res["st_101"]["reliability_score"] == 85.5


def test_get_stations_current_statuses_empty_or_none(station_service, status_dao):
    """Retourne {} si la liste est vide ou si aucune station n'est trouvée."""
    assert station_service.get_stations_current_statuses([]) == {}
    assert station_service.get_stations_current_statuses(["", None]) == {}

    status_dao.get_latest_statuses.return_value = {}
    assert station_service.get_stations_current_statuses(["st_unknown"]) == {}


# --- Tests de get_station_history() ---


def test_get_station_history_1h(station_service, status_dao, hourly_dao, sample_status, sample_hourly_status):
    """Récupère l'historique sur 1h."""
    status_dao.get_one_station_history.return_value = [sample_status]
    hourly_dao.get_hourly_stats.return_value = [sample_hourly_status]

    history = station_service.get_station_history("st_101", TimePeriod.une_heure)

    assert len(history) == 1
    assert history[0]["station_id"] == "st_101"
    assert history[0]["num_bikes_available"] == 10
    assert history[0]["reliability_score"] == 85.5


def test_get_station_history_1h_empty(station_service, status_dao):
    """Retourne [] si aucun statut n'est trouvé sur 1h."""
    status_dao.get_one_station_history.return_value = []
    assert station_service.get_station_history("st_101", TimePeriod.une_heure) == []


def test_get_station_history_24h(station_service, hourly_dao, sample_hourly_status):
    """Récupère l'historique horaire sur 24h avec calculs de ratios et durées moyennes."""
    zero_event_hourly = StationStatusHourly(
        station_id="st_101",
        bucket_hour=datetime(2026, 1, 1, 11, 0, tzinfo=UTC),
        sample_count=10,
        avg_operational_capacity=30.0,
        avg_num_bikes_available=15.0,
        avg_num_docks_available=15.0,
        empty_duration_sec=0,
        full_duration_sec=0,
        empty_events_cnt=0,
        full_events_cnt=0,
        reliability_score=100.0,
    )
    hourly_dao.get_hourly_stats.return_value = [sample_hourly_status, zero_event_hourly]

    history = station_service.get_station_history("st_101", TimePeriod.vingt_quatre_heures)

    assert len(history) == 2
    # Événements > 0
    assert history[0]["avg_full_duration"] == 300.0
    assert history[0]["avg_empty_duration"] == 300.0
    # Événements == 0
    assert history[1]["avg_full_duration"] == 0
    assert history[1]["avg_empty_duration"] == 0


def test_get_station_history_24h_empty(station_service, hourly_dao):
    """Retourne [] si aucune donnée horaire n'est trouvée sur 24h."""
    hourly_dao.get_hourly_stats.return_value = []
    assert station_service.get_station_history("st_101", TimePeriod.vingt_quatre_heures) == []


def test_get_station_history_daily(station_service, hourly_dao):
    """Récupère l'historique journalier agrégé pour 7j et 30j."""
    daily_records = [
        {
            "station_id": "st_101",
            "stat_date": date(2026, 1, 1),
            "avg_operational_capacity": 30.0,
            "avg_num_bikes_available": 10.0,
            "avg_num_docks_available": 20.0,
            "full_duration_sec": 7200,
            "empty_duration_sec": 1800,
            "full_events_cnt": 2,
            "empty_events_cnt": 1,
            "avg_reliability_score": 90.0,
        },
        {
            "station_id": "st_101",
            "stat_date": date(2026, 1, 2),
            "avg_operational_capacity": 30.0,
            "avg_num_bikes_available": 15.0,
            "avg_num_docks_available": 15.0,
            "full_duration_sec": 0,
            "empty_duration_sec": 0,
            "full_events_cnt": 0,
            "empty_events_cnt": 0,
            "avg_reliability_score": 100.0,
        },
    ]
    hourly_dao.aggregate_daily_stats.return_value = daily_records

    # Test 7 jours
    h7 = station_service.get_station_history("st_101", TimePeriod.sept_jours)
    assert len(h7) == 2
    assert h7[0]["avg_full_duration"] == 3600.0
    assert h7[1]["avg_full_duration"] == 0

    # Test 30 jours
    h30 = station_service.get_station_history("st_101", TimePeriod.trente_jours)
    assert len(h30) == 2

    # Cas vide
    hourly_dao.aggregate_daily_stats.return_value = []
    assert station_service.get_station_history("st_101", TimePeriod.sept_jours) == []


def test_get_station_history_invalid_period(station_service):
    """Retourne [] pour une période non reconnue."""
    assert station_service.get_station_history("st_101", "invalid_period") == []


# --- Tests de _matches_status_filters() ---


def test_matches_status_filters():
    """Vérifie le comportement des filtres de statut."""
    status = StationStatus(
        station_id="st_1",
        num_bikes_available=5,
        num_bikes_disabled=0,
        num_docks_available=15,
        num_docks_disabled=0,
        operational_capacity=20,
        last_reported=datetime.now(UTC),
        vehicle_types_available={"mechanical": 3, "electric": 2},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    )

    # Filtrage op_cap
    req_cap_ok = StationRecommendationRequest(lat=48.8, lon=2.3, op_cap=15)
    req_cap_fail = StationRecommendationRequest(lat=48.8, lon=2.3, op_cap=25)
    assert StationService._matches_status_filters(status, req_cap_ok) is True
    assert StationService._matches_status_filters(status, req_cap_fail) is False
    assert StationService._matches_status_filters(None, req_cap_ok) is False

    # Filtrage station_state
    req_state_ok = StationRecommendationRequest(lat=48.8, lon=2.3, station_state=StationState.FUNCTIONAL)
    req_state_fail = StationRecommendationRequest(lat=48.8, lon=2.3, station_state=StationState.EMPTY)
    assert StationService._matches_status_filters(status, req_state_ok) is True
    assert StationService._matches_status_filters(status, req_state_fail) is False
    assert StationService._matches_status_filters(None, req_state_ok) is False

    # Filtrage vehicle_type
    req_mech = StationRecommendationRequest(lat=48.8, lon=2.3, vehicle_type=VehicleTypeFilter.MECHANICAL)
    req_elec = StationRecommendationRequest(lat=48.8, lon=2.3, vehicle_type=VehicleTypeFilter.ELECTRIC)
    assert StationService._matches_status_filters(status, req_mech) is True
    assert StationService._matches_status_filters(status, req_elec) is True

    status_no_elec = StationStatus(
        station_id="st_2",
        num_bikes_available=3,
        num_bikes_disabled=0,
        num_docks_available=17,
        num_docks_disabled=0,
        operational_capacity=20,
        last_reported=datetime.now(UTC),
        vehicle_types_available={"mechanical": 3, "electric": 0},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    )
    assert StationService._matches_status_filters(status_no_elec, req_elec) is False
    assert StationService._matches_status_filters(None, req_mech) is False


# --- Tests de get_nearby_recommendations() ---


def test_get_nearby_recommendations_ok(
    station_service,
    station_dao,
    status_dao,
    hourly_dao,
    sample_station,
    sample_status,
    sample_hourly_status,
):
    """Recommande les stations à proximité triées par distance avec métriques agrégées."""
    # Station 2 plus proche
    station_close = StationInformation(
        station_id="st_close",
        name="Station Proche",
        short_name="CP",
        lat=48.8580,
        lon=2.3475,
        capacity=20,
    )
    status_close = StationStatus(
        station_id="st_close",
        num_bikes_available=5,
        num_bikes_disabled=0,
        num_docks_available=15,
        num_docks_disabled=0,
        operational_capacity=20,
        last_reported=datetime.now(UTC),
        vehicle_types_available={"mechanical": 5},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    )
    hourly_close = StationStatusHourly(
        station_id="st_close",
        bucket_hour=datetime.now(UTC),
        sample_count=10,
        avg_operational_capacity=20.0,
        avg_num_bikes_available=5.0,
        avg_num_docks_available=15.0,
        empty_duration_sec=0,
        full_duration_sec=0,
        empty_events_cnt=0,
        full_events_cnt=0,
        reliability_score=95.0,
    )

    station_dao.get_nearby.return_value = [sample_station, station_close]
    status_dao.get_latest_statuses.return_value = {
        "st_101": sample_status,
        "st_close": status_close,
    }
    hourly_dao.get_latest_hourly_statuses.return_value = {
        "st_101": sample_hourly_status,
        "st_close": hourly_close,
    }
    hourly_dao.aggregate_daily_stats_for_stations.return_value = {
        "st_101": [{"avg_reliability_score": 88.0}],
        "st_close": [{"avg_reliability_score": 96.0}],
    }

    req = StationRecommendationRequest(lat=48.8580, lon=2.3475, radius_meters=1000)
    recs = station_service.get_nearby_recommendations(req)

    assert len(recs) == 2
    # Tri par distance croissante (st_close est exactement aux coordonnées demandées)
    assert recs[0]["station_id"] == "st_close"
    assert recs[0]["distance_meters"] == pytest.approx(0.0, abs=1e-3)
    assert recs[0]["last_hour_reliability"] == 95.0
    assert recs[0]["last_day_reliability"] == 96.0

    assert recs[1]["station_id"] == "st_101"
    assert recs[1]["last_hour_reliability"] == 85.5
    assert recs[1]["last_day_reliability"] == 88.0


def test_get_nearby_recommendations_filters(
    station_service,
    station_dao,
    status_dao,
    hourly_dao,
    sample_station,
    sample_status,
    sample_hourly_status,
):
    """Filtre correctement selon le score de fiabilité minimal et les filtres de statut."""
    station_dao.get_nearby.return_value = [sample_station]
    status_dao.get_latest_statuses.return_value = {"st_101": sample_status}
    hourly_dao.get_latest_hourly_statuses.return_value = {"st_101": sample_hourly_status}
    hourly_dao.aggregate_daily_stats_for_stations.return_value = {}

    # Score min supérieur au score réel (85.5 < 90) -> exclus
    req_high_score = StationRecommendationRequest(lat=48.8, lon=2.3, score_min=90.0)
    assert station_service.get_nearby_recommendations(req_high_score) == []

    # Score min inférieur au score réel (85.5 >= 80) -> inclus
    req_low_score = StationRecommendationRequest(lat=48.8, lon=2.3, score_min=80.0)
    recs = station_service.get_nearby_recommendations(req_low_score)
    assert len(recs) == 1
    assert recs[0]["station_id"] == "st_101"


def test_get_nearby_recommendations_empty_cases(station_service, station_dao, status_dao, hourly_dao):
    """Gestion des cas où aucune station n'est à proximité ou toutes sont filtrées."""
    req = StationRecommendationRequest(lat=48.8, lon=2.3)

    # 1. Aucune station nearby
    station_dao.get_nearby.return_value = []
    assert station_service.get_nearby_recommendations(req) == []

    # 2. Station sans identifiant valide
    station_no_id = StationInformation(
        station_id=None,
        name="Sans ID",
        lat=48.8,
        lon=2.3,
        capacity=10,
    )
    station_dao.get_nearby.return_value = [station_no_id]
    assert station_service.get_nearby_recommendations(req) == []

    # 3. Toutes les stations filtrées par statut
    station_ok = StationInformation(
        station_id="st_1",
        name="Station 1",
        lat=48.8,
        lon=2.3,
        capacity=10,
    )
    station_dao.get_nearby.return_value = [station_ok]
    status_dao.get_latest_statuses.return_value = {}
    req_state = StationRecommendationRequest(lat=48.8, lon=2.3, station_state=StationState.EMPTY)
    assert station_service.get_nearby_recommendations(req_state) == []
