from datetime import datetime, timedelta
from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from business_object.station_status import StationStatus
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from service.recommendation_service import RecommendationService


def test_get_nearby_recommendations_ok():
    """Nous réussissons à obtenir des recommendations de stations
    à partir des critères donnés"""

    pass


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
