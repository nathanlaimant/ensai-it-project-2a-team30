from datetime import datetime

from fastapi import HTTPException

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO


class StationService:
    """
    Gère la logique métier liée à la consultation des stations.

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

    def get_by_id(self, station_id: str) -> StationInformation:
        """
        Donne une station à partir de son identifiant.

        Parameters
        ----------
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

        Parameters
        ----------
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

        Parameters
        ----------
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

        Parameters
        ----------
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
