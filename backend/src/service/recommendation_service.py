from datetime import timedelta

from haversine import haversine

from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO


class RecommendationService:
    """
    Gère la logique métier de recommandation de stations à proximité.

    Parameters
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

    def get_nearby_recommendations(self, lat: int, lon: int, radius_meters: int) -> list[dict]:
        """
        Recommande des stations à proximité d'une position donnée.

        Parameters
        ----------
        lat: int
            Latitude de l'adresse données

        longitude: int
            Longitude de l'adresse données

        radius_meters: int
            Rayon envisagé pour la recherche de stations

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
            statuses, hourly_stats, daily_stats = [], [], []
            for i in range(len(stations)):
                statuses[i] = StationStatusDAO().get_latest_status(stations[i].station_id)
                hourly_stats[i] = StationStatusHourlyDAO().get_hourly_stats(
                    stations[i].station_id,
                    statuses[i].last_reported,
                    statuses[i].last_reported - timedelta(hours=1)
                )
                daily_stats[i] = StationStatusHourlyDAO().get_daily_stats(
                    stations[i].station_id,
                    statuses[i].last_reported,
                    statuses[i].last_reported - timedelta(hours=1)
                )["avg_reliability_score"]

                la, lo = stations[i].lat, stations[i].lon
                res[i] = {
                    "station_id": stations[i].station_id,
                    "name": stations[i].station_id,
                    "distance_meters": haversine((la, lo), (lat, lon), unit='m'),
                    "hourly_reliability": hourly_stats[i].reliability_score,
                    "daily_reliability": daily_stats[i]
                }

        return res
