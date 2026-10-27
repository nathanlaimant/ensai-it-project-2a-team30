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

    def list_stations(self, query_params: dict) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.

        Parameters
        ----------
        query_params : dict
            Critères de filtrage et/ou de pagination.

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        return StationDAO().list_stations(query_params)

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
        start_time: datetime,
        end_time: datetime
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
            raise HTTPException(status_code=404, detail="Station introuvable")
        if start_time < end_time:
            raise HTTPException(status_code=400, detail="Horaires mal organisés")
        return StationStatusDAO().get_status_history(station_id, start_time, end_time)
