from ..dao import StationDAO, StationStatusDAO, StationStatusHourlyDAO


class RecommendationService:
    """Coordinate station recommendations."""

    def __init__(
        self,
        station_dao: StationDAO,
        status_dao: StationStatusDAO,
        hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_dao = station_dao
        self.status_dao = status_dao
        self.hourly_dao = hourly_dao

    def get_nearby_recommendations(self, query_params: dict) -> list[dict]:
        """Get nearby station recommendations."""
        raise NotImplementedError
