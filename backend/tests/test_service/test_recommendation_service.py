from datetime import datetime, timedelta
from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from business_object.station_status import StationStatus
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from service.recommendation_service import RecommendationService

stations_list = [
    StationInformation(
        station_id="19179944124",
        name="Hôpital Mondor",
        short_name="40001",
        lat=48.798922410229,
        lon=2.4537451531298,
        capacity=28
    ),
    StationInformation(
        station_id="18795078746",
        name=Charcot - Benfleet,
        short_name="32304",
        lat=48.878370277021,
        lon=2.440523876268,
        capacity=28
    )
]


def test_get_nearby_recommendations_ok():
    """Nous réussissons à obtenir des recommendations de stations
    à partir des critères donnés"""

    # GIVEN
    lat, lon, radius_meters = 48.7757567, 2.4456565, 40
    StationDAO().get_nearby = MagicMock(return_value=stations_list)

    # WHEN
    recos = RecommendationService().get_nearby_recommendations(lat, lon, radius_meters)

    # THEN
    assert isinstance(recos, list)
    for r in recos:
        assert isinstance(r, dict)


def test_get_nearby_recommendations_fail():
    """Nous échouons à obtenir des recommendations de stations à partir
    des critères donnés car l'un des arguments est impossible'"""

    # GIVEN
    lat, lon, radius_meters = 1.565657, 67575786.9898, 20
    StationDAO().get_nearby = MagicMock(return_value=None)

    # WHEN
    recos = RecommendationService().get_nearby_recommendations(
        lat, lon, radius_meters
    )

    # THEN
    assert recos is None
