from datetime import timedelta

from haversine import haversine

from business_object.station_state import StationState
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO


class RecommendationService:
    """
    Gère la logique métier de recommandation de stations à proximité.

    Attributes
    ----------
    station_dao : StationDAO
        DAO permettant l'accès aux informations fixes des stations.
    status_dao : StationStatusDAO
        DAO permettant l'accès aux statuts en temps réel des stations.
    hourly_dao : StationStatusHourlyDAO
        DAO permettant l'accès aux agrégations horaires des stations.
    """

    def __init__(
        self,
        station_dao: StationDAO,
        status_dao: StationStatusDAO,
        hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_dao = station_dao
        self.status_dao = status_dao
        self.hourly_dao = hourly_dao

    def get_nearby_recommendations(
        self,
        lat: int, lon: int, radius_meters: int,
        op_cap: int = None,
        station_state: StationState | str = None,
        score_min: float = None
    ) -> list[dict]:
        """
        Recommande des stations à proximité d'une position donnée.

        Arguments
        ---------
        lat: int
            Latitude de l'adresse données

        longitude: int
            Longitude de l'adresse données

        radius_meters: int
            Rayon envisagé pour la recherche de stations

        op_cap: int = None
            Capacité opérationnelle voulue pour la station

        station_state: StationState | str = None
            État global de la station
            (StationState.FULL, StationState.EMPTY, StationState.FUNCTIONAL)

        score_min: float = None
            Score de fiabilité minimal fixé pour la recherche

        Returns
        -------
        list of dict
            Liste des stations recommandées, avec leurs informations
            pertinentes (distance, disponibilité, fiabilité, etc.).
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        stations = StationDAO().get_nearby(lat, lon, radius_meters)

        res = None
        if stations:
            statuses, hourly_status, daily_reliability = [], [], []
            for i in range(len(stations)):
                statuses[i] = StationStatusDAO().get_latest_status(stations[i].station_id)
                hourly_status[i] = StationStatusHourlyDAO().get_hourly_stats(
                    stations[i].station_id,
                    statuses[i].last_reported,
                    statuses[i].last_reported - timedelta(hours=1)
                )[0]

                daily_reliability[i] = StationStatusHourlyDAO().get_daily_stats(
                    stations[i].station_id,
                    statuses[i].last_reported,
                    statuses[i].last_reported - timedelta(days=1)
                )[10]["avg_reliability_score"]

                la, lo = stations[i].lat, stations[i].lon
                res[i] = {
                    "station_id": stations[i].station_id,
                    "name": stations[i].station_id,
                    "distance_meters": haversine((la, lo), (lat, lon), unit='m'),
                    "operational_capacity": hourly_status[i].operational_capacity,
                    "station_state": hourly_status[i].station_state,
                    "last_hour_reliability": hourly_status[i].reliability_score,
                    "last_day_reliability": daily_reliability[i]
                }
                if hourly_status[i].operational_capacity < op_cap:
                    res.pop()
                if hourly_status[i].station_state != station_state:
                    res.pop()
                if hourly_status[i].reliability_score < score_min:
                    res.pop()
            sorted(res, key=lambda r: r["distance_meters"])
        return res
