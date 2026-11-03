from datetime import datetime, timedelta

from haversine import haversine

from business_object.station_information import StationInformation
from business_object.station_state import StationState
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO


class StationService:
    """
    Gère la logique métier liée à la consultation des stations.

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

    def get_by_id(self, station_id: str) -> StationInformation:
        """
        Donne une station à partir de son identifiant.

        Arguments
        ---------
        station_id: int
            Identifiant de la station à trouver

        Returns
        -------
        StationInformation
            Station avec l'identifiant correspondant.
        """
        return StationDAO().get_by_id(station_id)

    def list_stations(
        self,
        station_id: str = None,
        name: str = None,
        short_name: str = None,
        lat: int = None,
        lon: int = None,
        address: str = None,
        is_virtual_station: bool = None,
        contact_phone: str = None,
        capacity: int = None,
        is_charging_station: bool = None,
        nb_pages: int = None
    ) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.

        Arguments
        ---------
        station_id: str = None
            Identifiant de stations
        name: str = None
            Nom de station
        short_name: str = None
            Nom raccourci de station
        lat: int = None
            Latitude de station
        lon: int = None
            Longitude de station
        address: str = None
            Adresse de station
        is_virtual_station: bool = None
            Si True, lister les stations virtuelles
            Si False, lister les stations non virtuelles
        contact_phone: str = None
            Contact téléphonique de station
        capacity: int = None
            Capacité totale de la station
        is_charging_station: bool = None
            Si True, lister les stations avec bornes de charge
            Si False, ne pas lister les stations avec bornes de charge
        nb_pages: int = None
            Nombre de pages de stations à créer

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        return StationDAO().list_stations(
            station_id,
            name,
            short_name,
            lat,
            lon,
            address,
            is_virtual_station,
            contact_phone,
            capacity,
            is_charging_station,
            nb_pages
        )

    def get_station_current_status(self, station_id: str) -> dict:
        """
        Récupère l'état en temps réel d'une station.

        Arguments
        ---------
        station_id : str
            Identifiant de la station demandée.

        Returns
        -------
        dict
            État courant de la station (vélos/docks disponibles, etc.).
            Ne renvoie rien si la station n'est pas identifiable.
        """
        statut = StationStatusDAO().get_latest_status(station_id)
        return {
            "last_reported": statut.last_reported,
            "station_state": statut.station_state,
            "operational_capacity": statut.operational_capacity,
            "num_bikes_available": statut.num_bikes_available,
            "vehicule_types_available": statut.vehicule_types_available,
            "num_docks_available": statut.num_docks_available,
            "vehicule_docks_available": statut.vehicule_docks_available
        }

    def get_station_history(
        self,
        station_id: str,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> list[dict]:
        """
        Récupère l'historique d'état d'une station sur une période donnée.

        Arguments
        ---------
        station_id: str
            Identifiant de la station

        start_time: datetime
            Début de la période considérée pour la recherche

        end_time: datetime
            Fin de la période considérée pour la recherche

        Returns
        -------
        list of dict
            Historique des états de la station sur la période demandée.
            Ne renvoie rien si la station n'est pas identifiable, ou l'un des autres
            critères n'est pas dans le bon format.
        """
        station_exists = StationDAO().get_by_id(station_id)
        if not station_exists:
            return None
        if start_time > end_time:
            temp, start_time = start_time, end_time
            end_time = temp
        return StationStatusDAO().get_one_station_history(station_id, start_time, end_time)

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
